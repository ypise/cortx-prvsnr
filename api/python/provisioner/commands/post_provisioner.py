#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

from typing import List, Dict, Type, Optional
# import socket
import logging
import uuid
import os
from pathlib import Path

from .. import (
    inputs,
    config,
    profile,
    utils
)
from .bootstrap import (
    NodeGrains,
    Node
)
from ..vendor import attr
from ..errors import (
    ProvisionerError,
    SaltCmdResultError,
    SaltCmdRunError
)
from ..config import (
    ALL_MINIONS
)
from ..pillar import PillarUpdater
# TODO IMPROVE EOS-8473
from ..utils import (
    load_yaml,
    dump_yaml,
    load_yaml_str,
    repo_tgz,
    run_subprocess_cmd,
    node_hostname_validator
)
from ..ssh import keygen
from ..salt import SaltSSHClient
from .setup_gluster import SetupGluster
from . import (
    CommandParserFillerMixin
)
from .bootstrap_provisioner import (
    RunArgsSetup,
    BootstrapProvisioner,
    RunArgsSetupProvisionerGeneric,
    SetupCmdBase,
    SetupCtx,
    SetupCmdBase
)




logger = logging.getLogger(__name__)

add_pillar_merge_prefix = PillarUpdater.add_merge_prefix


@attr.s(auto_attribs=True)
class PostProvisioner(SetupCmdBase, CommandParserFillerMixin):
    input_type: Type[inputs.NoParams] = inputs.NoParams
    _run_args_type = RunArgsSetupProvisionerGeneric

    def run(self, nodes, **kwargs):  # noqa: C901 FIXME
        run_args = RunArgsSetupProvisionerGeneric(nodes=nodes, **kwargs)

        salt_logger = logging.getLogger('salt.fileclient')
        salt_logger.setLevel(logging.WARNING)

        # Config file validation against CLI args (Fail-Fast)
        if run_args.config_path:
            node_hostname_validator(run_args.nodes, run_args.config_path)
        else:
            # config.ini was not provided, possible replace_node call
            logger.warning(
                "config.ini was not provided, possible replace_node call."
                "Skipping validation."
            )

        # generate setup name
        setup_location = self.setup_location(run_args)
        setup_name = self.setup_name(run_args)

        # PREPARE FILE & PILLAR ROOTS

        logger.info(f"Starting to build setup '{setup_name}'")

        paths = config.profile_paths(
            config.profile_base_dir(
                location=setup_location, setup_name=setup_name
            )
        )

        ssh_client = BootstrapProvisioner()._create_ssh_client(
            paths['salt_master_file'], paths['salt_roster_file']
        )

        setup_ctx = SetupCtx(run_args, paths, ssh_client)

        master_targets = (
            ALL_MINIONS if run_args.ha else run_args.primary.minion_id
        )

        # Note. in both cases (ha and non-ha) we need user pillar update
        # only on primary node, in case of ha it would be shared for other
        # masters
        if not run_args.field_setup:
            logger.info("Updating release distribution type")
            ssh_client.cmd_run(
                (
                    'provisioner pillar_set --fpath release.sls'
                    f' release/type \'"{run_args.dist_type.value}"\''
                ), targets=run_args.primary.minion_id
            )

            if run_args.url_cortx_deps:
                logger.info("Setting url for bundled dependencies")
                ssh_client.cmd_run(
                    (
                        'provisioner pillar_set --fpath release.sls'
                        ' release/deps_bundle_url '
                        f'\'"{run_args.url_cortx_deps}"\''
                    ), targets=run_args.primary.minion_id
                )

            if run_args.target_build:
                logger.info("Updating target build pillar")
                ssh_client.cmd_run(
                    (
                        'provisioner pillar_set --fpath release.sls'
                        f' release/target_build \'"{run_args.target_build}"\''
                    ), targets=run_args.primary.minion_id
                )

            logger.info("Generating a password for the service user")

            service_user_password = utils.generate_random_secret()

            ssh_client.cmd_run(
                (
                    'provisioner pillar_set'
                    f' system/service-user/password '
                    f' \'"{service_user_password}"\''
                ),
                targets=run_args.primary.minion_id,
                secure=True
            )

        if run_args.target_build:
            # TODO IMPROVE non idempotent now
            logger.info("Get release factory version")
            if run_args.dist_type == config.DistrType.BUNDLE:
                url = f"{run_args.target_build}/cortx_iso"
            else:
                url = run_args.target_build

            if url.startswith(('http://', 'https://')):
                ssh_client.cmd_run(
                    (
                       f'curl {url}/RELEASE.INFO '
                       f'-o /etc/yum.repos.d/RELEASE_FACTORY.INFO'
                    )
                )
            elif url.startswith('file://'):
                # TODO TEST EOS-12076
                ssh_client.cmd_run(
                    (
                       f'cp -f {url[7:]}/RELEASE.INFO '
                       f'/etc/yum.repos.d/RELEASE_FACTORY.INFO'
                    )
                )
            else:
                raise ValueError(
                    f"Unexpected target build: {run_args.target_build}"
                )

        # TODO IMPROVE EOS-8473 FROM THAT POINT REMOTE SALT SYSTEM IS FULLY
        #      CONFIGURED AND MIGHT BE USED INSTEAD OF SALT-SSH BASED CONTROL

        logger.info("Sync salt modules")
        res = ssh_client.cmd_run("salt-call saltutil.list_extmods")
        logger.debug(f"Current list of extension modules: {res}")
        res = ssh_client.cmd_run("salt-call saltutil.sync_modules")
        logger.debug(f"Synced extension modules: {res}")

        logger.info("Configuring provisioner logging")
        if run_args.source in ('iso', 'rpm'):
            ssh_client.cmd_run(
                "salt-call state.apply components.system.prepare",
                targets=master_targets
            )

        # Seperation of variable to make flake8 happy
        ssh_client.cmd_run(
            (
                'provisioner pillar_set --fpath provisioner.sls '
                'provisioner/cluster_info/num_of_nodes '
                f"\"{len(run_args.nodes)}\""
            ), targets=run_args.primary.minion_id
        )

        # Grains data is not getting refreshed within sls files
        # if we call init.sls for machine_id states.
        logger.info("Refresh machine id on the system")
        for state in [
            'components.provisioner.config.machine_id.reset',
            'components.provisioner.config.machine_id.refresh_grains'
        ]:
            ssh_client.cmd_run(
                f"salt-call state.apply {state}",
                targets=ALL_MINIONS
            )

        inline_pillar = None
        if run_args.source == 'local':
            for pkg in [
                'rsyslog',
                'rsyslog-elasticsearch',
                'rsyslog-mmjsonparse'
            ]:
                ssh_client.cmd_run(
                    (
                        "provisioner pillar_set "
                        f"commons/version/{pkg} '\"latest\"'"
                    ), targets=run_args.primary.minion_id
                )
                inline_pillar = (
                    "{\"inline\": {\"no_encrypt\": True}}"
                )

        logger.info(
             "Encrypt pillar values and Refresh enclosure id on the system"
        )
        for state in [
            *(
                ()
                if run_args.source == 'local'
                else ('components.system.config.pillar_encrypt', )
            ),
            'components.system.storage.enclosure_id',
            'components.system.config.sync_salt'
        ]:
            ssh_client.cmd_run(
                f"salt-call state.apply {state}",
                targets=ALL_MINIONS
            )

        pillar = f"pillar='{inline_pillar}'" if inline_pillar else ""
        ssh_client.cmd_run(
            (
                "salt-call state.apply components.provisioner.config "
                f"{pillar}"
            ),
            targets=ALL_MINIONS
        )

        logger.info("Configuring provisioner for future updates")
        for node in run_args.nodes:
            ssh_client.state_apply(
                'update_post_boot',
                targets=node.minion_id
            )

        # TODO EOS-18920 Validation for node role
        # to execute cluster_id api

        logger.info("Setting unique ClusterID to pillar file "
                    f"on node: {run_args.primary.minion_id}")

        ssh_client.cmd_run(
            (
               "provisioner cluster_id"
            ), targets=run_args.primary.minion_id
        )


        logger.info("Done")

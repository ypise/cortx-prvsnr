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

from provisioner import set_hostname
from ..data.data_store import ConfStore

def get_from_confstore(index_name):
    """Fetch data from confstore file storage"""
    try:
        conf = ConfStore()
        data = conf.get_data(index_name = index_name)
    except Exception as exc:
        raise exc
    return data

class SetHostname():
    """Set hostname for the system"""

    def run(self, config_file = None):

        hostname=None        
        if config_file:
            hostname = get_from_confstore(index_name = 'hostname')
        try:
            set_hostname(hostname=hostname)
        except Exception as exc:
            raise exc

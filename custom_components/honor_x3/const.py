"""Constants for honor_x3."""
# Base component constants
DOMAIN = "honor_x3"
DOMAIN_DATA = "{}_data".format(DOMAIN)
VERSION = "v1.0.6"
PLATFORMS = ["sensor"]
ISSUE_URL = "https://github.com/juacas/honor_x3/issues"

STARTUP = """
-------------------------------------------------------------------
{name}
Version: {version}
This is a custom component
If you have any issues with this you need to open an issue here:
{issueurl}
-------------------------------------------------------------------
"""


# Icons
ICON = "mdi:router-wireless"


ICONS = {
    'DesktopComputer': 'mdi:desktop-classic',
    'laptop': 'mdi:laptop',
    'smartphone': 'mdi:cellphone-wireless',
    'game': 'mdi:gamepad-variant',
    'stb': 'mdi:television',
    'camera': 'mdi:cctv'
}
# Configuration
# CONF_NAME = "name"
# CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_NAME = "Honor X3 router"

# Interval in seconds
INTERVAL = 60

from mcp.server.fastmcp import FastMCP
from netmiko import ConnectHandler

mcp = FastMCP("net-tools")

DEVICES = {
    "R1":  {"host": "192.168.100.1"},
    "R2":  {"host": "192.168.100.2"},
    "SW1": {"host": "192.168.100.3"},
}
CREDS = {"device_type": "cisco_ios", "username": "cisco",
         "password": "cisco", "secret": "cisco"}

def _run_show(device, command):
    if device not in DEVICES:
        return f"Unknown device '{device}'. Known: {', '.join(DEVICES)}"
    if not command.strip().startswith("show"):
        return "Only 'show' commands are allowed (read-only)."
    conn = ConnectHandler(host=DEVICES[device]["host"], **CREDS)
    conn.enable()
    out = conn.send_command(command)
    conn.disconnect()
    return out

@mcp.tool()
def list_devices() -> str:
    """List the network devices this server can reach."""
    return ", ".join(DEVICES)

@mcp.tool()
def get_interfaces(device: str) -> str:
    """Show interface status (show ip interface brief) on a device (R1, R2, SW1)."""
    return _run_show(device, "show ip interface brief")

@mcp.tool()
def run_show_command(device: str, command: str) -> str:
    """Run any read-only 'show' command on a device and return its output."""
    return _run_show(device, command)

@mcp.tool()
def get_eigrp_neighbors(device: str) -> str:
    """Show the EIGRP neighbors on a router (R1 or R2)."""
    return _run_show(device, "show ip eigrp neighbors")

if __name__ == "__main__":
    mcp.run(transport="stdio")
from netmiko import ConnectHandler
from ntc_templates.parse import parse_output
import os

# Router IPs: 10.0.15.61 - 65
devices = {f"R{i+1}": f"10.0.15.{61+i}" for i in range(5)}

# Credential
USERNAME = os.getenv("ROUTER_USER", "admin")
PASSWORD = os.getenv("ROUTER_PASS", "cisco")  # default ถ้าไม่มี env

BASE_PARAMS = {
    "device_type": "cisco_ios",
    "username": USERNAME,
    "password": PASSWORD,
    "use_keys": False,
    "allow_agent": False,
    "disabled_algorithms": {
        "pubkeys": ["rsa-sha2-256", "rsa-sha2-512"],
        "kex": [
            "diffie-hellman-group1-sha1",
            "diffie-hellman-group14-sha256",
            "diffie-hellman-group16-sha512",
            "diffie-hellman-group18-sha512",
            "diffie-hellman-group-exchange-sha256",
            "ecdh-sha2-nistp256",
            "ecdh-sha2-nistp384",
            "ecdh-sha2-nistp521",
            "curve25519-sha256",
            "curve25519-sha256@libssh.org",
        ],
        "hostkeys": [
            "ssh-ed25519",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
        ],
    },
}


def get_ip_interfaces(name, ip):
    print(f"\nConnecting to {name} ({ip})...")
    params = BASE_PARAMS.copy()
    params["ip"] = ip
    conn = ConnectHandler(**params)
    conn.enable()

    # Run command
    output = conn.send_command("show ip interface brief")

    interfaces = parse_output(
        platform="cisco_ios", command="show ip interface brief", data=output
    )

    conn.disconnect()

    return {
        "router_ip": ip,
        "interfaces": interfaces,
    }


if __name__ == "__main__":
    for name, ip in devices.items():
        info = get_ip_interfaces(name, ip)
        print(f"{name} ({ip}) uptime: {info['uptime']}")
        for intf in info["interfaces"]:
            print(f"   {intf}")
    print("\nAll routers checked.")

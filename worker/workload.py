from netmiko import ConnectHandler
import subprocess

DEVICE_PARAMS = {
    "device_type": "cisco_ios",
    "ip": None,
    "username": None,
    "password": None,
}


def connect_to(ip, username, password):
    temp_params = DEVICE_PARAMS.copy()
    temp_params["ip"] = ip
    temp_params["username"] = username
    temp_params["password"] = password
    return temp_params


def show_interface(ip, username, password):
    with ConnectHandler(**connect_to(ip, username, password)) as ssh:
        output = ssh.send_command("show ip interface brief", use_textfsm=True)
        return output

def show_motd(ip, username, password):
    with ConnectHandler(**connect_to(ip, username, password)) as ssh:
        output = ssh.send_command("show banner motd", use_textfsm=True)
        return output


def create_motd(ip_address, username, password, motd_text=""):

    command = ['ansible-playbook', 'set_cisco_router_motd_playbook.yaml',
               '-i', f'{ip_address},',
               '-u', f'{username}',
               '-e', f'ansible_password="{password}"',
               '-e', f'custom_motd="{motd_text}"']


    # Run ansible-playbook
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout + result.stderr
    print(output)
    
    # Check for successful execution
    if 'failed=0' in output and ('changed=' in output or 'ok=' in output):
        return("Ok: success")
    else:
        return("Error: Ansible")


def create_loopback(ip_address, username, password, loopback_number, loopback_ip):

    command = ['ansible-playbook', 'create_loopback_playbook.yaml',
               '-i', f'{ip_address},',
               '-u', f'{username}',
               '-e', f'ansible_password="{password}"',
               '-e', f'loopback_number="{loopback_number}"',
               '-e', f'loopback_ip="{loopback_ip}"']


    # Run ansible-playbook
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout + result.stderr
    print(output)
    
    # Check for successful execution
    if 'failed=0' in output and ('changed=' in output or 'ok=' in output):
        return("Ok: success")
    else:
        return("Error: Ansible")


def delete_loopback(ip_address, username, password, loopback_number):

    command = ['ansible-playbook', 'delete_loopback_playbook.yaml',
               '-i', f'{ip_address},',
               '-u', f'{username}',
               '-e', f'ansible_password="{password}"',
               '-e', f'loopback_number="{loopback_number}"']


    # Run ansible-playbook
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout + result.stderr
    print(output)
    
    # Check for successful execution
    if 'failed=0' in output and ('changed=' in output or 'ok=' in output):
        return("Ok: success")
    else:
        return("Error: Ansible")
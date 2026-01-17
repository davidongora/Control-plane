"""Service management utilities for Nginx, Gunicorn, and databases."""
import re
import json
from typing import Dict, List, Optional, Tuple
from .ssh_manager import SSHConnectionManager


class ServiceManager:
    """Manages services on remote servers via SSH."""
    
    def __init__(self, ssh_manager: SSHConnectionManager):
        self.ssh = ssh_manager
    
    def get_service_status(self, service_name: str) -> Dict:
        """Get status of a systemd service."""
        command = f"systemctl status {service_name} --no-pager"
        exit_code, stdout, stderr = self.ssh.execute_command(command)
        
        status = {
            'service': service_name,
            'is_running': False,
            'status': 'unknown',
            'pid': None,
            'memory': None,
        }
        
        if exit_code == 0 or 'Active:' in stdout:
            if 'Active: active (running)' in stdout:
                status['is_running'] = True
                status['status'] = 'running'
            elif 'Active: inactive' in stdout:
                status['status'] = 'stopped'
            elif 'Active: failed' in stdout:
                status['status'] = 'failed'
            
            # Extract PID
            pid_match = re.search(r'Main PID: (\d+)', stdout)
            if pid_match:
                status['pid'] = int(pid_match.group(1))
            
            # Extract memory
            mem_match = re.search(r'Memory: ([\d.]+)([KMG])', stdout)
            if mem_match:
                mem_value = float(mem_match.group(1))
                mem_unit = mem_match.group(2)
                if mem_unit == 'K':
                    status['memory'] = mem_value / 1024
                elif mem_unit == 'M':
                    status['memory'] = mem_value
                elif mem_unit == 'G':
                    status['memory'] = mem_value * 1024
        
        return status
    
    def start_service(self, service_name: str) -> bool:
        """Start a systemd service."""
        command = f"sudo systemctl start {service_name}"
        exit_code, stdout, stderr = self.ssh.execute_command(command)
        return exit_code == 0
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a systemd service."""
        command = f"sudo systemctl stop {service_name}"
        exit_code, stdout, stderr = self.ssh.execute_command(command)
        return exit_code == 0
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a systemd service."""
        command = f"sudo systemctl restart {service_name}"
        exit_code, stdout, stderr = self.ssh.execute_command(command)
        return exit_code == 0
    
    def get_running_processes(self) -> List[Dict]:
        """Get list of running processes with resource usage."""
        command = "ps aux --sort=-%mem | head -20"
        exit_code, stdout, stderr = self.ssh.execute_command(command)
        
        processes = []
        if exit_code == 0:
            lines = stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                parts = line.split()
                if len(parts) >= 11:
                    processes.append({
                        'user': parts[0],
                        'pid': parts[1],
                        'cpu': parts[2],
                        'mem': parts[3],
                        'command': ' '.join(parts[10:]),
                    })
        
        return processes


class NginxManager:
    """Manages Nginx configuration and operations."""
    
    def __init__(self, ssh_manager: SSHConnectionManager):
        self.ssh = ssh_manager
        self.sites_available = "/etc/nginx/sites-available"
        self.sites_enabled = "/etc/nginx/sites-enabled"
    
    def list_sites(self) -> Dict[str, List[str]]:
        """List all Nginx sites (available and enabled)."""
        available_cmd = f"ls {self.sites_available} 2>/dev/null || echo ''"
        enabled_cmd = f"ls {self.sites_enabled} 2>/dev/null || echo ''"
        
        _, available_out, _ = self.ssh.execute_command(available_cmd)
        _, enabled_out, _ = self.ssh.execute_command(enabled_cmd)
        
        return {
            'available': [s.strip() for s in available_out.split('\n') if s.strip() and s != 'default'],
            'enabled': [s.strip() for s in enabled_out.split('\n') if s.strip() and s != 'default'],
        }
    
    def get_site_config(self, site_name: str) -> Optional[str]:
        """Get configuration content for a site."""
        command = f"cat {self.sites_available}/{site_name}"
        exit_code, stdout, stderr = self.ssh.execute_command(command)
        return stdout if exit_code == 0 else None
    
    def enable_site(self, site_name: str) -> bool:
        """Enable an Nginx site."""
        command = f"sudo ln -sf {self.sites_available}/{site_name} {self.sites_enabled}/{site_name}"
        exit_code, _, _ = self.ssh.execute_command(command)
        if exit_code == 0:
            return self.reload_nginx()
        return False
    
    def disable_site(self, site_name: str) -> bool:
        """Disable an Nginx site."""
        command = f"sudo rm -f {self.sites_enabled}/{site_name}"
        exit_code, _, _ = self.ssh.execute_command(command)
        if exit_code == 0:
            return self.reload_nginx()
        return False
    
    def test_config(self) -> Tuple[bool, str]:
        """Test Nginx configuration."""
        command = "sudo nginx -t"
        exit_code, stdout, stderr = self.ssh.execute_command(command)
        return exit_code == 0, stderr + stdout
    
    def reload_nginx(self) -> bool:
        """Reload Nginx configuration."""
        command = "sudo systemctl reload nginx"
        exit_code, _, _ = self.ssh.execute_command(command)
        return exit_code == 0


class GunicornManager:
    """Manages Gunicorn processes."""
    
    def __init__(self, ssh_manager: SSHConnectionManager):
        self.ssh = ssh_manager
    
    def list_processes(self) -> List[Dict]:
        """List all running Gunicorn processes."""
        command = "ps aux | grep gunicorn | grep -v grep"
        exit_code, stdout, stderr = self.ssh.execute_command(command)
        
        processes = []
        if stdout:
            for line in stdout.strip().split('\n'):
                parts = line.split()
                if len(parts) >= 11:
                    processes.append({
                        'user': parts[0],
                        'pid': parts[1],
                        'cpu': parts[2],
                        'mem': parts[3],
                        'start_time': parts[8],
                        'command': ' '.join(parts[10:]),
                    })
        
        return processes
    
    def get_process_info(self, pid: int) -> Optional[Dict]:
        """Get detailed information about a Gunicorn process."""
        command = f"ps -p {pid} -o pid,ppid,user,%cpu,%mem,etime,command --no-headers"
        exit_code, stdout, stderr = self.ssh.execute_command(command)
        
        if exit_code == 0 and stdout:
            parts = stdout.strip().split()
            if len(parts) >= 7:
                return {
                    'pid': parts[0],
                    'ppid': parts[1],
                    'user': parts[2],
                    'cpu': parts[3],
                    'mem': parts[4],
                    'elapsed_time': parts[5],
                    'command': ' '.join(parts[6:]),
                }
        
        return None
    
    def restart_process(self, service_name: str) -> bool:
        """Restart a Gunicorn service."""
        command = f"sudo systemctl restart {service_name}"
        exit_code, _, _ = self.ssh.execute_command(command)
        return exit_code == 0


class DatabaseManager:
    """Manages database operations."""
    
    def __init__(self, ssh_manager: SSHConnectionManager):
        self.ssh = ssh_manager
    
    def get_postgres_databases(self) -> List[str]:
        """List PostgreSQL databases."""
        command = "sudo -u postgres psql -l -t | cut -d'|' -f1 | grep -v '^$' | sed 's/ //g'"
        exit_code, stdout, stderr = self.ssh.execute_command(command)
        
        if exit_code == 0:
            return [db.strip() for db in stdout.split('\n') if db.strip() and db.strip() not in ['template0', 'template1']]
        return []
    
    def get_mysql_databases(self) -> List[str]:
        """List MySQL databases."""
        command = "mysql -e 'SHOW DATABASES;' | tail -n +2"
        exit_code, stdout, stderr = self.ssh.execute_command(command)
        
        if exit_code == 0:
            return [db.strip() for db in stdout.split('\n') if db.strip() and db.strip() not in ['information_schema', 'mysql', 'performance_schema', 'sys']]
        return []

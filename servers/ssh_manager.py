"""SSH Connection Manager for remote server operations."""
import paramiko
import io
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class SSHConnectionManager:
    """Manages SSH connections to remote servers."""
    
    def __init__(self, hostname: str, port: int, username: str, 
                 password: Optional[str] = None, ssh_key: Optional[str] = None):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.ssh_key = ssh_key
        self.client = None
    
    def connect(self) -> bool:
        """Establish SSH connection to the server."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.ssh_key:
                private_key = paramiko.RSAKey.from_private_key(io.StringIO(self.ssh_key))
                self.client.connect(
                    self.hostname,
                    port=self.port,
                    username=self.username,
                    pkey=private_key,
                    timeout=10
                )
            elif self.password:
                self.client.connect(
                    self.hostname,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=10
                )
            else:
                logger.error("No authentication method provided")
                return False
            
            logger.info(f"Successfully connected to {self.hostname}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to {self.hostname}: {str(e)}")
            return False
    
    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """Execute a command on the remote server.
        
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if not self.client:
            return -1, "", "Not connected to server"
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            stdout_str = stdout.read().decode('utf-8')
            stderr_str = stderr.read().decode('utf-8')
            return exit_code, stdout_str, stderr_str
        except Exception as e:
            logger.error(f"Failed to execute command '{command}': {str(e)}")
            return -1, "", str(e)
    
    def disconnect(self):
        """Close the SSH connection."""
        if self.client:
            self.client.close()
            self.client = None
            logger.info(f"Disconnected from {self.hostname}")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

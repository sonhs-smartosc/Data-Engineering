install aws cli for ubuntu 

1. `sudo yum remove awscli`
2. `curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"`
3. `unzip awscliv2.zip`
4. `sudo ./aws/install`
5. check version `aws --version`

document: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

+ setup aws configure

1. `aws configure`
    -> get apikey: https://docs.aws.amazon.com/IAM/latest/UserGuide/access-key-self-managed.html

   
+ create key pair: `aws ec2 create-key-pair --key-name sonhs-key --query "KeyMaterial" --output text > aws-key.pem`
`chmod 400 aws-key.pem`
  

+ connect to server: `https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-linux-inst-ssh.html`

-> connect ssh: ssh -i ./aws-key.pem ec2-user@43.207.202.74 


+ install package for instance aws 
    + docker : 
      + `sudo yum update -y`
      + `sudo yum install -y docker`
      + `sudo service docker start`
      + `sudo systemctl enable docker`
      + `mkdir -p ~/.docker/cli-plugins/`
      + `curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m) -o ~/.docker/cli-plugins/docker-compose`
      + `chmod +x ~/.docker/cli-plugins/docker-compose`
      + `docker compose version`
      + `sudo usermod -a -G docker $USER`
      + `newgrp docker`
    + git:
      + sudo yum install -y git


    
+ Azure:

install azure cli: 
    `sudo apt update`
    `sudo apt install -y ca-certificates curl apt-transport-https lsb-release gnupg`
    `curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /usr/share/keyrings/microsoft.gpg > /dev/null`
    `echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/azure-cli.list`
    `sudo apt update`
    `sudo apt install -y azure-cli`

check az version
    az version

azure login
    `az login`
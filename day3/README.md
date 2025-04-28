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

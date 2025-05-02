terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "ap-northeast-1"
}

resource "aws_instance" "sonhs_test_terraform" {
  ami           = "ami-05206bf8aecfc7ae6"
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.allow_http_ssh_https_custom.id]

  key_name = "aws-instance-key"
  tags = {
    Name = "ExampleAppServerInstance"
  }
}

resource "aws_security_group" "allow_http_ssh_https_custom" {
  name        = "allow_http_ssh_https_custom"
  description = "Allow HTTP, SSH, HTTPS, custom ports"

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 433
    to_port     = 433
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Custom port 5000"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
Learn
    + Terraform là một công cụ mã nguồn mở được sử dụng để tự động hóa việc quản lý cơ sở hạ tầng trong lĩnh vực DevOps. Do HashiCorp phát triển,
    Terraform cho phép bạn mô tả cấu hình hạ tầng của mình dưới dạng mã (Infrastructure as Code - IaC) bằng cách sử dụng ngôn ngữ cấu hình HashiCorp Configuration Language (HCL) hoặc JSON. 

install Terraform ubuntu
    1.  `sudo apt-get install -y gnupg software-properties-common`

    2. `wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg`

    3. `sudo apt-get update`
        `sudo apt-get install terraform`

    4. ` terraform --version`
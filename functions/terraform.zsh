# Terraform utility functions
# Shortcuts for common terraform workflows

# Terraform init with auto-detection of backend.hcl and terraform.tfvars
# Usage: tfi
tfi() {
    if [ ! -f "backend.hcl" ]; then
        echo "❌ Error: backend.hcl not found in current directory"
        return 1
    fi
    
    if [ ! -f "terraform.tfvars" ]; then
        echo "❌ Error: terraform.tfvars not found in current directory"
        return 1
    fi
    
    echo "✅ Found backend.hcl and terraform.tfvars"
    terraform init -reconfigure -backend-config=backend.hcl
}

# Terraform plan with tfvars
# Usage: tfp
tfp() {
    if [ ! -f "terraform.tfvars" ]; then
        echo "❌ Error: terraform.tfvars not found in current directory"
        return 1
    fi
    
    terraform plan -var-file=terraform.tfvars
}

# Terraform apply with tfvars
# Usage: tfa
tfa() {
    if [ ! -f "terraform.tfvars" ]; then
        echo "❌ Error: terraform.tfvars not found in current directory"
        return 1
    fi
    
    terraform apply -var-file=terraform.tfvars
}

# Terraform apply auto-approve with tfvars
# Usage: tfaa
tfaa() {
    if [ ! -f "terraform.tfvars" ]; then
        echo "❌ Error: terraform.tfvars not found in current directory"
        return 1
    fi
    
    echo "⚠️  This will auto-approve terraform apply"
    read -q "REPLY?Continue? (y/n) "
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply -var-file=terraform.tfvars -auto-approve
    else
        echo "Cancelled"
        return 1
    fi
}

# Terraform validate
# Usage: tfv
tfv() {
    terraform validate
}

# Terraform fmt (format)
# Usage: tff
tff() {
    terraform fmt -recursive
}

# Terraform state list
# Usage: tfsl
tfsl() {
    terraform state list
}


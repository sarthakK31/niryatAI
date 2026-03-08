#!/bin/bash
# ================================================
# Niryat AI - EC2 Instance Setup Script
# Run this ON the EC2 instance after SSH-ing in
# ================================================
set -e

echo "=== Niryat AI EC2 Setup ==="

# 1. System updates and Docker install
echo "[1/5] Installing Docker..."
sudo yum update -y
sudo yum install -y docker git postgresql15
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 2. Clone repo
echo "[2/5] Cloning repository..."
cd /home/ec2-user
if [ ! -d "niryatAI" ]; then
    git clone https://github.com/YOUR_USERNAME/niryatAI.git
fi
cd niryatAI

# 3. Create production .env
echo "[3/5] Setting up environment..."
echo "Create your .env file at /home/ec2-user/niryatAI/backend/.env"
echo "Use backend/.env.production.template as reference"
echo ""
echo "IMPORTANT: Run these commands to create your .env:"
echo "  cd /home/ec2-user/niryatAI/backend"
echo "  cp .env.production.template .env"
echo "  nano .env   # edit with your actual values"
echo ""

# 4. Init database on RDS
echo "[4/5] Database setup instructions:"
echo "  psql -h YOUR_RDS_ENDPOINT -U postgres -d niryatdb -f db-init/01-schema.sql"
echo "  Then run your data ingestion scripts to load market intelligence data"
echo ""

# 5. Build and run
echo "[5/5] Build and run with Docker..."
echo "  cd /home/ec2-user/niryatAI/backend"
echo "  docker build -t niryat-backend ."
echo "  docker run -d --name niryat-api -p 8000:8000 --env-file .env niryat-backend"
echo ""
echo "=== Setup complete. Test with: curl http://localhost:8000/health ==="

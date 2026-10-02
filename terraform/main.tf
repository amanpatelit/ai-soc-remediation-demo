provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Create demo S3 Bucket
resource "aws_s3_bucket" "demo_bucket" {
  bucket        = "devops-ai-soc-demo-${random_id.bucket_suffix.hex}"
  force_destroy = true
}

# Intentionally Vulnerable Configuration: Public Access Block Disabled
resource "aws_s3_bucket_public_access_block" "vulnerable_block" {
  bucket = aws_s3_bucket.demo_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
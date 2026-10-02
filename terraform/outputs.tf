output "bucket_name" {
  value       = aws_s3_bucket.demo_bucket.id
  description = "The name of the created public S3 bucket"
}
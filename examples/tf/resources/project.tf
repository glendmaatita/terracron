resource "supabase_project" "primary" {
  organization_id   = "continued-brown-smelt"
  name              = "foo"
  database_password = "bar"
  region            = "us-east-1"
  instance_size     = "micro"
}
# https://registry.terraform.io/providers/supabase/supabase/latest/docs
provider "supabase" {
  access_token = "" // overrided by terracron
}

# https://terraform.io/language/settings/backends/gcs
terraform {
  backend "local" {
    path = "/opt/data/terraform.tfstate"
  }

  required_providers {
    supabase = {
        source = "supabase/supabase"
        version = "1.5.1"
    }
  }
}
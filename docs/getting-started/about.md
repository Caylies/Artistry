# What is Artistry?

**Artistry** is a Ballsdex package designed for managing community-made art. It is inspired by the community art system previously used in the official Ballsdex server, and supersedes "Art-BD-Package", which was a community-made art manager for Ballsdex versions predating 3.0.

## Installation

Artistry can be installed by adding the following code into your `config/extra.toml` file:

```toml
[[ballsdex.packages]]
location = "git+https://github.com/Caylies/Artistry.git@1.1.1"
path = "artistry"
enabled = true
```

Once the TOML entry is added, you may now rebuild and start your bot!

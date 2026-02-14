import toml

with open("/servers/25565/forwarding.secret", "r") as f:
    forward_secret = f.read().strip()

with open("config/features.toml", "r") as f:
    features = toml.load(f)
    features['networking']['proxy']['enabled'] = True
    features['networking']['proxy']['velocity']['enabled'] = True
    features['networking']['proxy']['velocity']['secret'] = forward_secret

with open("config/features.toml", "w") as f:
    toml.dump(features, f)

print("Proxy configuration updated.")
chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=_-'
CIPHER_WHEEL_N = {}
CIPHER_WHEEL_L = {}

for i in range(len(chars)):
    CIPHER_WHEEL_N[i] = chars[i]
    CIPHER_WHEEL_L[chars[i]] = i

print(f"mod length: {len(CIPHER_WHEEL_N)}")
print(f"CIPHER_WHEEL_N = {CIPHER_WHEEL_N}")
print(f"CIPHER_WHEEL_L = {CIPHER_WHEEL_L}\n")

print("If you want bytes dicts:")
bytes_n = {k: v.encode() for k, v in CIPHER_WHEEL_N.items()}
bytes_l = {k.encode(): v for k, v in CIPHER_WHEEL_L.items()}
print(f"CIPHER_WHEEL_N = {bytes_n}")
print(f"CIPHER_WHEEL_L = {bytes_l}")


# with open('/home/nbroyles/Documents/logs2105.7z.robo', 'r') as f:
#     content = f.read()
#
# possible_chars = set([char for char in content])
#
# print(possible_chars)

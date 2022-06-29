from my_dep import a

from questionpy.sdk.registry import registry

print("Hello from example package.")
registry["this came from my_dep"] = a

# Examples

## Basic Examples

### Hello World
```np
print("Namaste Nepal")
```

### Variables
```np
naam = "Diwas"
umar = 20
print(naam)
print(umar)
```

### Arithmetic
```np
print(3 + 4)
print(10 * 5)
print(20 / 4)
```

### Conditions
```np
age = 20
if age >= 18:
    print("Adult")
else:
    print("Minor")
```

### Loops
```np
for i in 10:
    print(i)
```

### Functions
```np
def add(a, b):
    return a + b

print(add(3, 4))
```

### Lists
```np
items = [1, 2, 3, 4, 5]
print(items)
print(len(items))
```

### Maps
```np
user = {"name": "Diwas", "age": 20}
print(user)
```

## Advanced Examples

### Using Math Library
```np
import ganit

print(ganit.sqrt(25))
print(ganit.power(2, 3))
print(ganit.jod(10, 20))
```

### File Operations
```np
import file

file.write("test.txt", "Hello World")
content = file.read("test.txt")
print(content)
```

### JSON Operations
```np
import jsonlib

data = {"name": "Diwas", "age": 20}
json_text = jsonlib.stringify(data)
print(json_text)

parsed = jsonlib.parse(json_text)
print(parsed)
```

### Random Numbers
```np
import randomlib

print(randomlib.number(1, 100))
print(randomlib.choice(["Ram", "Sita", "Diwas"]))
```

## Nepali Syntax Examples

### Nepali Keywords
```np
yedi umar >= 18:
    print("Adult")
natra:
    print("Minor")
```

### Nepali Functions
```np
kaam jod(a, b):
    firta a + b

print(jod(3, 4))
```

### Nepali Loops
```np
ko_lagi i ma 10:
    print(i)
```

## Complete Demo

See `examples/demo.np` for a comprehensive example showing all major features.
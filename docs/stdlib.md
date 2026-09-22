# Standard Library

## ganit (Math)

Mathematical operations.

```np
import ganit

ganit.jod(a, b)      # Addition
ganit.ghata(a, b)    # Subtraction
ganit.guna(a, b)     # Multiplication
ganit.bhag(a, b)     # Division
ganit.sqrt(x)        # Square root
ganit.power(x, y)    # Power
```

## samaya (Time)

Time and date operations.

```np
import samaya

samaya.now()         # Current time
samaya.today()       # Today's date
samaya.sleep(secs)   # Sleep
samaya.format(time, format_string)  # Format time
```

## file

File operations.

```np
import file

file.write(filename, content)  # Write to file
file.read(filename)           # Read from file
file.exists(filename)         # Check if file exists
file.delete(filename)         # Delete file
file.copy(source, target)     # Copy file
file.move(source, target)     # Move file
```

## folder

Folder operations.

```np
import folder

folder.create(path)    # Create folder
folder.exists(path)    # Check if folder exists
folder.list(path)      # List contents
folder.delete(path)    # Delete folder
```

## system

System information.

```np
import system

system.os_name()       # Operating system
system.platform_name() # Platform
system.hostname()      # Hostname
system.username()      # Username
```

## randomlib

Random number generation.

```np
import randomlib

randomlib.number(min, max)   # Random number
randomlib.choice(items)      # Random choice
randomlib.shuffle(items)     # Shuffle list
```

## jsonlib

JSON operations.

```np
import jsonlib

jsonlib.parse(text)          # Parse JSON string
jsonlib.stringify(data)      # Convert to JSON string
jsonlib.read(filename)       # Read JSON from file
jsonlib.write(filename, data) # Write JSON to file
```
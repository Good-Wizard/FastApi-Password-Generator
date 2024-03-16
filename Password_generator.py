
from fastapi import FastAPI, HTTPException
import random
import string
from pydantic import BaseModel, Field, validator

app = FastAPI()

# Define a Pydantic model for the password options
class PasswordOptions(BaseModel):
    length: int = Field(16, gt=0)  # The length of the password
    use_special_chars: bool = False  # Whether to include special characters
    use_uppercase: bool = True  # Whether to include uppercase letters
    use_lowercase: bool = True  # Whether to include lowercase letters
    use_digits: bool = True  # Whether to include digits
    excluded_chars: str = ''  # Characters to exclude from the password
    start_with_letter: bool = True  # Whether the password should start with a letter

    # Validate the length of the password
    @validator('length')
    def validate_length(cls, v):
        if v < 8 or v > 100:
            raise HTTPException(status_code=400, detail='Password length must be between 8 to 100')
        return v

    # Validate excluded characters
    @validator('excluded_chars')
    def validate_excluded_chars(cls, v):
        for char in v:
            if char not in string.printable:
                raise ValueError('[ Error  ]', 'Excluded characters must be printable')
        return v

# Define the password generator endpoint
@app.post("/password-generator/")
def generate_password(options: PasswordOptions):
    # Initialize an empty string for the characters to include in the password
    chars = ''

    # Add uppercase letters if use_uppercase is True
    if options.use_uppercase:
        chars += string.ascii_uppercase

    # Add lowercase letters if use_lowercase is True
    if options.use_lowercase:
        chars += string.ascii_lowercase

    # Add digits if use_digits is True
    if options.use_digits:
        chars += string.digits

    # Add special characters if use_special_chars is True
    if options.use_special_chars:
        chars += string.punctuation

    # Remove excluded characters
    chars = ''.join(c for c in chars if c not in options.excluded_chars)

    # Ensure the password starts with a letter if required
    if options.start_with_letter:
        first_char = random.choice(string.ascii_letters)
        password = first_char + ''.join(random.choice(chars) for _ in range(options.length - 1))
    else:
        # Generate the password
        password = ''.join(random.choice(chars) for _ in range(options.length))

    # Return the password
    try:
        if len(password) < 12:
            strength = "Weak"
        elif len(password) < 16:
            strength = "Medium"
        elif len(password) >= 16:
            strength = "Strong"
        return {"Strength": strength, "Generated Password": password}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
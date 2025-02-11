#Acer
# Basic offset
BASE_X_OFFSET = -7
Y_OFFSET = -10

def calculate_x_offset(x):
    """Calculate progressive X offset based on X coordinate"""
    # Start with base offset
    offset = BASE_X_OFFSET
    
    # Add -15 for every 250 pixels
    offset += -8  * (x // 31)    
    return offset
def calculate_y_offset(y):
    """Calculate progressive X offset based on X coordinate"""
    # Start with base offset
    offset = Y_OFFSET
    
    # Add -15 for every 250 pixels
    offset += -8 * (y // 31)
    
#HP

# Basic offset
BASE_X_OFFSET = -10
Y_OFFSET = -10

def calculate_x_offset(x):
    """Calculate progressive X offset based on X coordinate"""
    # Start with base offset
    offset = BASE_X_OFFSET
    
    # Add -15 for every 250 pixels
    offset += -5  * (x // 31)    
    return offset
def calculate_y_offset(y):
    """Calculate progressive X offset based on X coordinate"""
    # Start with base offset
    offset = Y_OFFSET
    
    # Add -15 for every 250 pixels
    offset += -5 * (y // 31)
    
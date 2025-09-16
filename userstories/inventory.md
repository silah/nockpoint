# Inventory User Stories (Current System)

## As a Club Member

### Equipment Browsing and Search
- **As a member**, I want to view all club equipment in a paginated list (20 items per page) so I can see what's available
- **As a member**, I want to search for equipment by name or description to find specific items
- **As a member**, I want to filter equipment by category to see only items of interest (bows, arrows, targets, etc.)
- **As a member**, I want to see basic item information including name, description, quantity, unit, location, and condition
- **As a member**, I want to view detailed item information including purchase date, price, and notes

### Equipment Information Access
- **As a member**, I want to view detailed equipment specifications including category-specific attributes
- **As a member**, I want to see equipment condition status (excellent, good, fair, poor, out of service)
- **As a member**, I want to see where equipment is located for easy retrieval
- **As a member**, I want to see equipment quantities to understand availability
- **As a member**, I want to access equipment notes that may contain usage instructions or warnings

### Category Viewing
- **As a member**, I want to view all equipment categories to understand how items are organized
- **As a member**, I want to see category descriptions to understand what belongs in each category
- **As a member**, I want to filter the inventory by category to focus on specific types of equipment

## As an Admin

### Equipment Management
- **As an admin**, I want to create new inventory items with complete details (name, description, quantity, unit, location, purchase info, condition, notes)
- **As an admin**, I want to edit existing inventory items to update any information
- **As an admin**, I want to delete inventory items that are no longer needed
- **As an admin**, I want to assign equipment to categories for better organization

### Category Management
- **As an admin**, I want to create new equipment categories with names and descriptions
- **As an admin**, I want to edit existing categories to update their information
- **As an admin**, I want to organize the inventory using a logical category system

### Category-Specific Attributes
- **As an admin**, I want to add bow-specific attributes (bow type, draw weight, draw length, handedness) when creating bow items
- **As an admin**, I want to add arrow-specific attributes (length, spine, point weight, fletching) when creating arrow items
- **As an admin**, I want to add target-specific attributes (size, type, material) when creating target items
- **As an admin**, I want different forms to appear based on the selected category for appropriate attribute capture

### Equipment Tracking
- **As an admin**, I want to track equipment purchase dates and prices for asset management
- **As an admin**, I want to monitor equipment condition and update it as needed
- **As an admin**, I want to record equipment locations to help with organization
- **As an admin**, I want to maintain equipment quantities and units of measurement

## Current System Implementation

### Inventory Workflow
1. **Category Setup**: Admin creates equipment categories with names and descriptions
2. **Item Creation**: Admin adds items with basic details and category-specific attributes
3. **Item Management**: Admin can edit/delete items and update information as needed
4. **Member Access**: All members can browse, search, and view detailed item information

### Technical Architecture (Current Implementation)
- **Database Models**: InventoryItem and InventoryCategory with JSON attribute storage
- **Category System**: Flexible category structure with custom attributes for different equipment types
- **Search Functionality**: Text search across item names and descriptions
- **Filtering**: Category-based filtering and pagination for large inventories
- **Form System**: Dynamic forms based on category selection (BowForm, ArrowForm, TargetForm)

### User Interface (Current Pages)
- **Inventory List** (`/inventory/`): Paginated equipment list with search and category filtering
- **Item Details** (`/inventory/item/<id>`): Detailed view of individual equipment items
- **Item Form** (`/inventory/new`, `/inventory/item/<id>/edit`): Admin item creation/editing with category-specific forms
- **Category List** (`/inventory/categories`): List of all equipment categories
- **Category Form** (`/inventory/categories/new`, `/inventory/categories/<id>/edit`): Admin category creation/editing

### Equipment Categories (Current System)
The system supports multiple equipment categories with specific attributes:
- **Bows**: Type (recurve/compound/traditional), draw weight, draw length, handedness
- **Arrows**: Length, spine, point weight, fletching description
- **Targets**: Size, type, material properties
- **General Equipment**: Standard attributes without category-specific fields

### Search and Filtering (Current Implementation)
- **Text Search**: Searches item names and descriptions simultaneously
- **Category Filter**: Dropdown filter to show items from specific categories only
- **Pagination**: 20 items per page with navigation controls
- **Combined Filtering**: Search and category filters work together

### Access Control (Current System)
- **Members**: Can view inventory list, search, filter, and view item details
- **Admins**: Full inventory management including create, edit, delete items and categories
- **Authentication**: All inventory functions require login with `@login_required`
- **Authorization**: Admin functions protected with `@admin_required` decorator

### Data Management (Current Features)
- **Item Tracking**: Complete item lifecycle from creation to deletion
- **Attribute Storage**: JSON-based storage for category-specific attributes
- **Condition Tracking**: Standardized condition values for all equipment
- **Location Management**: Text-based location tracking for equipment placement
- **Purchase Information**: Date and price tracking for asset management

### Key Features Not Implemented
The current inventory system does NOT include:
- Equipment reservation or checkout functionality
- Member equipment usage tracking or history
- Maintenance scheduling or repair tracking
- Equipment availability status or booking system
- Photo upload or visual equipment catalog
- Barcode/QR code scanning or automated tracking
- Equipment condition change history or audit trails
- Integration with external asset management systems
- Member equipment requests or purchase suggestions
- Equipment sharing between members or clubs

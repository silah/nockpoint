# Nockpoint Landing Site

A standalone static website for the Nockpoint Archery Club Management System. This site presents the application features and includes a signup form for archery clubs interested in using the system.

## Features

- **Responsive Design**: Built with Bootstrap 5 for mobile-first responsive design
- **Visual Consistency**: Matches the styling of the main Flask application
- **Club Signup Form**: Comprehensive form for club registration with validation
- **Pro Features Showcase**: Highlights both basic and pro feature offerings
- **Interactive Elements**: Smooth scrolling, hover effects, and form animations

## Structure

```
landing-site/
├── index.html          # Main landing page
├── css/
│   └── style.css       # Custom styles matching the Flask app
├── js/
│   └── main.js         # Interactive functionality and form handling
└── README.md           # This file
```

## Form Fields

The club signup form includes:

### Required Fields
- **Club Name**: Name of the archery club
- **Contact Person**: Primary contact for the club
- **Contact Email**: Email address for communication
- **State/County**: Geographic location (state/county level)
- **Country**: Country selection dropdown

### Optional Fields
- **Contact Phone**: Phone number for the contact person
- **Member Count**: Approximate number of club members
- **Club Type**: Type of archery (target, field, traditional, mixed)
- **Pro Plan**: Checkbox to indicate interest in pro features
- **Additional Information**: Free text field for specific needs or questions

## Technologies Used

- **HTML5**: Semantic markup with accessibility considerations
- **Bootstrap 5**: UI framework for responsive design and components
- **Bootstrap Icons**: Icon library for consistent iconography
- **Vanilla JavaScript**: Form validation, animations, and interactions
- **CSS3**: Custom styling and animations

## Form Handling

Currently, the form submission is handled client-side with console logging for development purposes. The form data is collected into a JavaScript object with the following structure:

```javascript
{
    clubName: "Example Archery Club",
    contactPerson: "John Doe",
    contactEmail: "john@example.com",
    contactPhone: "+1234567890",
    state: "California",
    country: "US",
    memberCount: "26-50",
    clubType: "target",
    proPlan: true,
    additionalInfo: "We're interested in tournament management features."
}
```

## Customization

### Styling
The site uses the same color scheme and styling as the main Flask application:
- Primary color: `#0d6efd` (Bootstrap blue)
- Consistent typography and spacing
- Matching card shadows and hover effects

### Form Integration
To integrate with a backend service:
1. Replace the `setTimeout` simulation in `js/main.js`
2. Add actual API endpoint for form submission
3. Implement proper error handling for failed submissions
4. Add success/failure messaging based on server response

### Content Updates
- Modify feature descriptions in the `#features` section
- Update pricing information in the `#pricing` section
- Customize the hero section messaging
- Add or remove form fields as needed

## Deployment

This is a completely static site that can be deployed to:
- GitHub Pages
- Netlify
- Vercel
- Any static hosting service
- CDN or web server

Simply upload the entire `landing-site` folder to your hosting provider.

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile responsive design
- Progressive enhancement for older browsers

## Development

To work on the site locally:
1. Open `index.html` in a web browser
2. Use a local development server for better experience:
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js
   npx serve .
   ```
3. Access at `http://localhost:8000`

## Form Validation

The form includes:
- Required field validation
- Email format validation
- Real-time error display
- Accessible error messaging
- Visual feedback for form states

## Accessibility

- Semantic HTML structure
- Proper form labels and associations
- Keyboard navigation support
- Screen reader friendly
- High contrast support
- Focus management

## Future Enhancements

- Add form submission to actual backend
- Implement email notifications
- Add more detailed feature comparisons
- Include customer testimonials
- Add multi-language support
- Integrate with payment processing for pro subscriptions
# Responsive Design Guide for Arkos AI

This guide outlines the responsive design principles and implementation strategies for the Arkos AI web interface. It provides guidelines for ensuring that the UI adapts well to different screen sizes and devices.

## Table of Contents

1. [Introduction](#introduction)
2. [Responsive Design Principles](#responsive-design-principles)
3. [Breakpoints](#breakpoints)
4. [Responsive Utility Classes](#responsive-utility-classes)
5. [Layout Patterns](#layout-patterns)
6. [Component-Specific Guidelines](#component-specific-guidelines)
7. [Testing Responsive Design](#testing-responsive-design)
8. [Best Practices](#best-practices)

## Introduction

Responsive design ensures that the Arkos AI web interface provides an optimal viewing and interaction experience across a wide range of devices, from desktop computers to mobile phones. This guide provides a framework for implementing responsive design throughout the application.

## Responsive Design Principles

The Arkos AI web interface follows these core responsive design principles:

1. **Fluid Layouts**: Use relative units (%, rem, em) instead of fixed units (px) for layout dimensions.
2. **Flexible Images and Media**: Ensure that images and media scale appropriately for different screen sizes.
3. **Media Queries**: Use CSS media queries to apply different styles based on device characteristics.
4. **Mobile-First Approach**: Design for mobile devices first, then enhance for larger screens.
5. **Touch-Friendly Interfaces**: Ensure that interactive elements are large enough for touch interaction on mobile devices.
6. **Progressive Enhancement**: Provide a basic experience for all devices, then enhance for devices with more capabilities.
7. **Performance Optimization**: Optimize performance for all devices, especially for mobile devices with limited resources.

## Breakpoints

The Arkos AI web interface uses the following breakpoints:

| Breakpoint | Width (px) | Description |
|------------|------------|-------------|
| xs         | 480px      | Extra small devices (phones) |
| sm         | 640px      | Small devices (large phones, small tablets) |
| md         | 768px      | Medium devices (tablets) |
| lg         | 1024px     | Large devices (desktops) |
| xl         | 1280px     | Extra large devices (large desktops) |
| 2xl        | 1440px     | 2x extra large devices |
| 3xl        | 1920px     | 3x extra large devices |
| 2k         | 2560px     | 2K resolution devices |
| 4k         | 3180px     | 4K resolution devices |

These breakpoints are defined in the `tailwind.config.cjs` file and can be used with Tailwind's responsive utilities.

## Responsive Utility Classes

The Arkos AI web interface provides a set of responsive utility classes in `src/styles/responsive-utils.css`. These classes can be used to implement responsive design without writing custom CSS.

### Container Classes

```html
<div class="container-responsive">
  <!-- Content here -->
</div>
```

The `container-responsive` class provides a responsive container with appropriate padding for different screen sizes.

### Spacing Classes

```html
<div class="spacing-responsive">
  <!-- Content here -->
</div>
```

The `spacing-responsive` class provides responsive padding for different screen sizes.

### Typography Classes

```html
<h1 class="text-responsive-title">Title</h1>
<h2 class="text-responsive-subtitle">Subtitle</h2>
<p class="text-responsive-body">Body text</p>
<span class="text-responsive-small">Small text</span>
```

These classes provide responsive typography with appropriate font sizes for different screen sizes.

### Grid Classes

```html
<div class="grid-responsive-1">
  <!-- 1 column on all screen sizes -->
</div>

<div class="grid-responsive-2">
  <!-- 1 column on small screens, 2 columns on larger screens -->
</div>

<div class="grid-responsive-3">
  <!-- 1 column on small screens, 2 columns on medium screens, 3 columns on large screens -->
</div>

<div class="grid-responsive-4">
  <!-- 1 column on small screens, 2 columns on medium screens, 3 columns on large screens, 4 columns on extra large screens -->
</div>
```

These classes provide responsive grid layouts with appropriate column counts for different screen sizes.

### Flex Classes

```html
<div class="flex-responsive-row">
  <!-- Flex column on small screens, flex row on larger screens -->
</div>

<div class="flex-responsive-col">
  <!-- Flex column on all screen sizes -->
</div>
```

These classes provide responsive flex layouts with appropriate flex direction for different screen sizes.

### Gap Classes

```html
<div class="gap-responsive">
  <!-- Responsive gap for grid and flex layouts -->
</div>
```

The `gap-responsive` class provides responsive gap spacing for grid and flex layouts.

### Visibility Classes

```html
<div class="hidden-xs">
  <!-- Hidden on extra small screens, visible on larger screens -->
</div>

<div class="visible-xs">
  <!-- Visible on extra small screens, hidden on larger screens -->
</div>
```

These classes provide responsive visibility control for different screen sizes.

### Orientation-Specific Classes

```html
<div class="portrait-only">
  <!-- Visible only in portrait orientation -->
</div>

<div class="landscape-only">
  <!-- Visible only in landscape orientation -->
</div>
```

These classes provide orientation-specific visibility control.

## Layout Patterns

### Responsive Grid Layout

For a responsive grid layout, use the following pattern:

```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-responsive">
  <!-- Grid items here -->
</div>
```

This creates a grid with 1 column on small screens, 2 columns on medium screens, 3 columns on large screens, and 4 columns on extra large screens.

### Responsive Flex Layout

For a responsive flex layout, use the following pattern:

```html
<div class="flex flex-col sm:flex-row gap-responsive">
  <!-- Flex items here -->
</div>
```

This creates a flex container with a column layout on small screens and a row layout on larger screens.

### Responsive Card Layout

For a responsive card layout, use the following pattern:

```html
<div class="grid-responsive-3 gap-responsive">
  <div class="card-responsive">
    <!-- Card content here -->
  </div>
  <!-- More cards here -->
</div>
```

This creates a responsive grid of cards with appropriate spacing and styling for different screen sizes.

## Component-Specific Guidelines

### Navigation

- Use a hamburger menu for small screens and a horizontal menu for larger screens.
- Ensure that navigation items have sufficient touch targets on mobile devices.
- Consider using a bottom navigation bar for mobile devices.

```html
<!-- Desktop navigation -->
<nav class="hidden sm:flex">
  <!-- Navigation items here -->
</nav>

<!-- Mobile navigation -->
<nav class="flex sm:hidden">
  <!-- Hamburger menu or bottom navigation here -->
</nav>
```

### Forms

- Use full-width form controls on small screens and appropriate widths on larger screens.
- Ensure that form controls have sufficient touch targets on mobile devices.
- Consider using a single-column layout for forms on small screens and a multi-column layout on larger screens.

```html
<form class="grid grid-cols-1 md:grid-cols-2 gap-responsive">
  <!-- Form controls here -->
</form>
```

### Tables

- Use responsive tables that can be scrolled horizontally on small screens.
- Consider using a card-based layout for tables on small screens.
- Ensure that table cells have sufficient touch targets on mobile devices.

```html
<div class="overflow-x-auto">
  <table class="table-responsive">
    <!-- Table content here -->
  </table>
</div>
```

### Images

- Use responsive images that scale appropriately for different screen sizes.
- Consider using different image sizes for different screen sizes using the `srcset` attribute.
- Ensure that images have appropriate aspect ratios for different screen sizes.

```html
<img
  class="w-full h-auto"
  src="image.jpg"
  srcset="image-small.jpg 480w, image-medium.jpg 768w, image-large.jpg 1024w"
  sizes="(max-width: 480px) 100vw, (max-width: 768px) 50vw, 33vw"
  alt="Description"
/>
```

### Buttons

- Use appropriate button sizes for different screen sizes.
- Ensure that buttons have sufficient touch targets on mobile devices.
- Consider using full-width buttons on small screens and appropriate widths on larger screens.

```html
<button class="btn-responsive">
  Button Text
</button>
```

### Modals and Dialogs

- Use appropriate modal sizes for different screen sizes.
- Ensure that modals and dialogs are fully visible on small screens.
- Consider using full-screen modals on small screens and centered modals on larger screens.

```html
<div class="modal-responsive">
  <!-- Modal content here -->
</div>
```

### Camera Views

- Use a grid layout for camera views on larger screens and a list layout on smaller screens.
- Ensure that camera views have appropriate aspect ratios for different screen sizes.
- Consider using a single camera view on small screens and multiple camera views on larger screens.

```html
<div class="grid-responsive-3 gap-responsive">
  <!-- Camera views here -->
</div>
```

## Testing Responsive Design

To ensure that the Arkos AI web interface provides an optimal experience across all devices, test the responsive design using the following methods:

1. **Browser Developer Tools**: Use the responsive design mode in browser developer tools to test different screen sizes and device types.
2. **Real Devices**: Test on actual devices, including phones, tablets, and desktops, to ensure that the interface works as expected.
3. **Automated Testing**: Use automated testing tools to test the responsive design across a wide range of devices and screen sizes.
4. **User Testing**: Conduct user testing on different devices to gather feedback on the responsive design.

## Best Practices

Follow these best practices to ensure that the Arkos AI web interface provides an optimal responsive experience:

1. **Use Relative Units**: Use relative units (%, rem, em) instead of fixed units (px) for layout dimensions.
2. **Test on Real Devices**: Test the responsive design on actual devices, not just in browser developer tools.
3. **Optimize Performance**: Optimize performance for all devices, especially for mobile devices with limited resources.
4. **Consider Touch Interaction**: Ensure that interactive elements are large enough for touch interaction on mobile devices.
5. **Use Appropriate Font Sizes**: Use appropriate font sizes for different screen sizes to ensure readability.
6. **Provide Sufficient Contrast**: Ensure that text and interactive elements have sufficient contrast for readability.
7. **Use Appropriate Spacing**: Use appropriate spacing for different screen sizes to ensure that content is not too crowded or too sparse.
8. **Consider Orientation Changes**: Ensure that the interface works well in both portrait and landscape orientations.
9. **Use Feature Detection**: Use feature detection instead of device detection to ensure that the interface works well on all devices.
10. **Progressive Enhancement**: Provide a basic experience for all devices, then enhance for devices with more capabilities.

## Implementation Examples

### Example 1: Responsive Dashboard

```tsx
import { cn } from "@/lib/utils";
import { isMobile } from "react-device-detect";

function Dashboard() {
  return (
    <div className="container-responsive">
      <h1 className="text-responsive-title">Dashboard</h1>
      
      {/* Responsive grid layout */}
      <div className="grid-responsive-3 gap-responsive mt-4">
        {/* Card 1 */}
        <div className="card-responsive">
          <h2 className="text-responsive-subtitle">Card 1</h2>
          <p className="text-responsive-body">Card content</p>
        </div>
        
        {/* Card 2 */}
        <div className="card-responsive">
          <h2 className="text-responsive-subtitle">Card 2</h2>
          <p className="text-responsive-body">Card content</p>
        </div>
        
        {/* Card 3 */}
        <div className="card-responsive">
          <h2 className="text-responsive-subtitle">Card 3</h2>
          <p className="text-responsive-body">Card content</p>
        </div>
      </div>
      
      {/* Responsive flex layout */}
      <div className="flex-responsive-row gap-responsive mt-6">
        <div className="w-full sm:w-1/2">
          <h2 className="text-responsive-subtitle">Section 1</h2>
          <p className="text-responsive-body">Section content</p>
        </div>
        
        <div className="w-full sm:w-1/2">
          <h2 className="text-responsive-subtitle">Section 2</h2>
          <p className="text-responsive-body">Section content</p>
        </div>
      </div>
      
      {/* Device-specific content */}
      <div className="mt-6">
        <div className="visible-xs">
          <p className="text-responsive-body">This content is only visible on mobile devices.</p>
        </div>
        
        <div className="hidden-xs">
          <p className="text-responsive-body">This content is only visible on larger devices.</p>
        </div>
      </div>
    </div>
  );
}
```

### Example 2: Responsive Camera View

```tsx
import { cn } from "@/lib/utils";
import { isMobile } from "react-device-detect";
import { useState } from "react";

function CameraView() {
  const [layout, setLayout] = useState<"grid" | "list">(isMobile ? "list" : "grid");
  
  return (
    <div className="container-responsive">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-responsive-title">Cameras</h1>
        
        <div className="flex gap-2">
          <button
            className={cn(
              "p-2 rounded",
              layout === "grid" ? "bg-primary text-white" : "bg-secondary"
            )}
            onClick={() => setLayout("grid")}
          >
            Grid
          </button>
          
          <button
            className={cn(
              "p-2 rounded",
              layout === "list" ? "bg-primary text-white" : "bg-secondary"
            )}
            onClick={() => setLayout("list")}
          >
            List
          </button>
        </div>
      </div>
      
      {layout === "grid" ? (
        <div className="grid-responsive-3 gap-responsive">
          {/* Camera 1 */}
          <div className="aspect-video bg-black rounded-lg overflow-hidden">
            <img src="camera1.jpg" alt="Camera 1" className="w-full h-full object-cover" />
          </div>
          
          {/* Camera 2 */}
          <div className="aspect-video bg-black rounded-lg overflow-hidden">
            <img src="camera2.jpg" alt="Camera 2" className="w-full h-full object-cover" />
          </div>
          
          {/* Camera 3 */}
          <div className="aspect-video bg-black rounded-lg overflow-hidden">
            <img src="camera3.jpg" alt="Camera 3" className="w-full h-full object-cover" />
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-responsive">
          {/* Camera 1 */}
          <div className="flex-responsive-row gap-2 items-center">
            <div className="w-full sm:w-1/3 aspect-video bg-black rounded-lg overflow-hidden">
              <img src="camera1.jpg" alt="Camera 1" className="w-full h-full object-cover" />
            </div>
            
            <div className="w-full sm:w-2/3">
              <h2 className="text-responsive-subtitle">Camera 1</h2>
              <p className="text-responsive-body">Camera details</p>
            </div>
          </div>
          
          {/* Camera 2 */}
          <div className="flex-responsive-row gap-2 items-center">
            <div className="w-full sm:w-1/3 aspect-video bg-black rounded-lg overflow-hidden">
              <img src="camera2.jpg" alt="Camera 2" className="w-full h-full object-cover" />
            </div>
            
            <div className="w-full sm:w-2/3">
              <h2 className="text-responsive-subtitle">Camera 2</h2>
              <p className="text-responsive-body">Camera details</p>
            </div>
          </div>
          
          {/* Camera 3 */}
          <div className="flex-responsive-row gap-2 items-center">
            <div className="w-full sm:w-1/3 aspect-video bg-black rounded-lg overflow-hidden">
              <img src="camera3.jpg" alt="Camera 3" className="w-full h-full object-cover" />
            </div>
            
            <div className="w-full sm:w-2/3">
              <h2 className="text-responsive-subtitle">Camera 3</h2>
              <p className="text-responsive-body">Camera details</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

## Conclusion

By following the guidelines and using the responsive utility classes provided in this guide, you can ensure that the Arkos AI web interface provides an optimal viewing and interaction experience across a wide range of devices. Remember to test your responsive design on actual devices and gather feedback from users to continuously improve the responsive experience.

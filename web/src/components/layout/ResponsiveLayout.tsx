import { cn } from "@/lib/utils";
import { isMobile, isTablet } from "react-device-detect";
import { ReactNode } from "react";

type ResponsiveLayoutProps = {
  children: ReactNode;
  className?: string;
  fullWidth?: boolean;
  fullHeight?: boolean;
  centered?: boolean;
  padded?: boolean;
  gap?: "none" | "small" | "medium" | "large";
  direction?: "row" | "column" | "responsive";
  breakpoint?: "xs" | "sm" | "md" | "lg" | "xl";
};

/**
 * ResponsiveLayout - A flexible container component that adapts to different screen sizes
 * 
 * @param children - The content to render inside the layout
 * @param className - Additional CSS classes to apply
 * @param fullWidth - Whether the layout should take up the full width of its container
 * @param fullHeight - Whether the layout should take up the full height of its container
 * @param centered - Whether the content should be centered horizontally and vertically
 * @param padded - Whether the layout should have padding
 * @param gap - The size of the gap between children
 * @param direction - The flex direction of the layout
 * @param breakpoint - The breakpoint at which the layout should change from column to row (if direction is "responsive")
 */
export function ResponsiveLayout({
  children,
  className,
  fullWidth = false,
  fullHeight = false,
  centered = false,
  padded = false,
  gap = "medium",
  direction = "column",
  breakpoint = "md",
}: ResponsiveLayoutProps) {
  // Map gap sizes to Tailwind classes
  const gapClasses = {
    none: "",
    small: "gap-2 sm:gap-3",
    medium: "gap-3 sm:gap-4 md:gap-6",
    large: "gap-4 sm:gap-6 md:gap-8",
  };

  // Map breakpoints to Tailwind classes for responsive direction
  const breakpointClasses = {
    xs: "flex-col xs:flex-row",
    sm: "flex-col sm:flex-row",
    md: "flex-col md:flex-row",
    lg: "flex-col lg:flex-row",
    xl: "flex-col xl:flex-row",
  };

  // Determine the flex direction class
  const directionClass = direction === "responsive" 
    ? breakpointClasses[breakpoint]
    : direction === "row" ? "flex-row" : "flex-col";

  return (
    <div
      className={cn(
        "flex",
        directionClass,
        gapClasses[gap],
        fullWidth && "w-full",
        fullHeight && "h-full",
        centered && "items-center justify-center",
        padded && "container-padding-responsive",
        className
      )}
    >
      {children}
    </div>
  );
}

type ResponsiveContainerProps = {
  children: ReactNode;
  className?: string;
  maxWidth?: "none" | "xs" | "sm" | "md" | "lg" | "xl" | "2xl" | "full";
  centered?: boolean;
  padded?: boolean;
};

/**
 * ResponsiveContainer - A container component with responsive max-width constraints
 * 
 * @param children - The content to render inside the container
 * @param className - Additional CSS classes to apply
 * @param maxWidth - The maximum width of the container
 * @param centered - Whether the container should be centered horizontally
 * @param padded - Whether the container should have padding
 */
export function ResponsiveContainer({
  children,
  className,
  maxWidth = "xl",
  centered = true,
  padded = true,
}: ResponsiveContainerProps) {
  // Map max width to Tailwind classes
  const maxWidthClasses = {
    none: "",
    xs: "max-w-xs",
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    "2xl": "max-w-2xl",
    full: "max-w-full",
  };

  return (
    <div
      className={cn(
        "w-full",
        maxWidthClasses[maxWidth],
        centered && "mx-auto",
        padded && "container-padding-responsive",
        className
      )}
    >
      {children}
    </div>
  );
}

type ResponsiveGridProps = {
  children: ReactNode;
  className?: string;
  columns?: 1 | 2 | 3 | 4 | 6 | 12;
  gap?: "none" | "small" | "medium" | "large";
  padded?: boolean;
};

/**
 * ResponsiveGrid - A grid layout that adapts to different screen sizes
 * 
 * @param children - The content to render inside the grid
 * @param className - Additional CSS classes to apply
 * @param columns - The maximum number of columns in the grid
 * @param gap - The size of the gap between grid items
 * @param padded - Whether the grid should have padding
 */
export function ResponsiveGrid({
  children,
  className,
  columns = 3,
  gap = "medium",
  padded = false,
}: ResponsiveGridProps) {
  // Map gap sizes to Tailwind classes
  const gapClasses = {
    none: "",
    small: "gap-2 sm:gap-3",
    medium: "gap-3 sm:gap-4 md:gap-6",
    large: "gap-4 sm:gap-6 md:gap-8",
  };

  // Map columns to Tailwind classes
  const columnClasses = {
    1: "grid-cols-1",
    2: "grid-cols-1 sm:grid-cols-2",
    3: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3",
    4: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4",
    6: "grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6",
    12: "grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 2xl:grid-cols-12",
  };

  return (
    <div
      className={cn(
        "grid",
        columnClasses[columns],
        gapClasses[gap],
        padded && "container-padding-responsive",
        className
      )}
    >
      {children}
    </div>
  );
}

type ResponsiveSectionProps = {
  children: ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  padded?: boolean;
  bordered?: boolean;
  rounded?: boolean;
  shadowed?: boolean;
};

/**
 * ResponsiveSection - A section component with responsive styling
 * 
 * @param children - The content to render inside the section
 * @param className - Additional CSS classes to apply
 * @param title - The title of the section
 * @param subtitle - The subtitle of the section
 * @param padded - Whether the section should have padding
 * @param bordered - Whether the section should have a border
 * @param rounded - Whether the section should have rounded corners
 * @param shadowed - Whether the section should have a shadow
 */
export function ResponsiveSection({
  children,
  className,
  title,
  subtitle,
  padded = true,
  bordered = false,
  rounded = true,
  shadowed = false,
}: ResponsiveSectionProps) {
  return (
    <section
      className={cn(
        padded && "spacing-responsive",
        bordered && "border",
        rounded && "rounded-responsive",
        shadowed && "shadow-responsive",
        className
      )}
    >
      {title && (
        <h2 className="text-responsive-title mb-2">{title}</h2>
      )}
      {subtitle && (
        <p className="text-responsive-small text-muted-foreground mb-4">{subtitle}</p>
      )}
      {children}
    </section>
  );
}

type ResponsiveCardProps = {
  children: ReactNode;
  className?: string;
  padded?: boolean;
  bordered?: boolean;
  rounded?: boolean;
  shadowed?: boolean;
  onClick?: () => void;
  hoverable?: boolean;
};

/**
 * ResponsiveCard - A card component with responsive styling
 * 
 * @param children - The content to render inside the card
 * @param className - Additional CSS classes to apply
 * @param padded - Whether the card should have padding
 * @param bordered - Whether the card should have a border
 * @param rounded - Whether the card should have rounded corners
 * @param shadowed - Whether the card should have a shadow
 * @param onClick - Function to call when the card is clicked
 * @param hoverable - Whether the card should have hover effects
 */
export function ResponsiveCard({
  children,
  className,
  padded = true,
  bordered = true,
  rounded = true,
  shadowed = true,
  onClick,
  hoverable = false,
}: ResponsiveCardProps) {
  return (
    <div
      className={cn(
        "bg-card text-card-foreground",
        padded && "p-3 sm:p-4 md:p-5",
        bordered && "border",
        rounded && "rounded-lg md:rounded-xl",
        shadowed && "shadow-sm sm:shadow md:shadow-md",
        hoverable && "transition-all duration-200 hover:shadow-md hover:scale-[1.01]",
        onClick && "cursor-pointer",
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  );
}

type DeviceSpecificProps = {
  children: ReactNode;
  className?: string;
  showOn: "mobile" | "tablet" | "desktop" | "mobile-tablet" | "tablet-desktop" | "all";
};

/**
 * DeviceSpecific - A component that only renders its children on specific device types
 * 
 * @param children - The content to render
 * @param className - Additional CSS classes to apply
 * @param showOn - The device types on which to show the content
 */
export function DeviceSpecific({
  children,
  className,
  showOn = "all",
}: DeviceSpecificProps) {
  // Determine if the content should be shown based on the current device
  const shouldShow = () => {
    switch (showOn) {
      case "mobile":
        return isMobile && !isTablet;
      case "tablet":
        return isTablet;
      case "desktop":
        return !isMobile && !isTablet;
      case "mobile-tablet":
        return isMobile || isTablet;
      case "tablet-desktop":
        return isTablet || (!isMobile && !isTablet);
      case "all":
        return true;
      default:
        return true;
    }
  };

  // If the content shouldn't be shown, return null
  if (!shouldShow()) {
    return null;
  }

  // Otherwise, render the children
  return (
    <div className={className}>
      {children}
    </div>
  );
}

type OrientationSpecificProps = {
  children: ReactNode;
  className?: string;
  orientation: "portrait" | "landscape" | "both";
};

/**
 * OrientationSpecific - A component that only renders its children in specific screen orientations
 * 
 * @param children - The content to render
 * @param className - Additional CSS classes to apply
 * @param orientation - The orientation in which to show the content
 */
export function OrientationSpecific({
  children,
  className,
  orientation = "both",
}: OrientationSpecificProps) {
  return (
    <div
      className={cn(
        orientation === "portrait" && "portrait-only",
        orientation === "landscape" && "landscape-only",
        className
      )}
    >
      {children}
    </div>
  );
}

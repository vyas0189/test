-----

## name: salt-design-system
description: Build React applications using JPMC Salt Design System. Use when creating React UIs with Salt components, implementing Salt themes (light/dark mode), configuring density settings, building forms, or any request mentioning “Salt”, “@salt-ds”, “JPMC design system”, or J.P. Morgan design patterns. Covers installation, SaltProvider setup, core components (Button, Input, FormField, Menu, Dialog, etc.), theming with design tokens, accessibility best practices, and layout patterns.

# JPMC Salt Design System

Build accessible, professional React applications with J.P. Morgan’s open-source Salt Design System.

## Quick Start

### Installation

```bash
npm install @salt-ds/core @salt-ds/theme @salt-ds/icons
# Optional: lab components (unstable)
npm install @salt-ds/lab
```

### Required Fonts

Add to `index.html`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
  href="https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,300;1,400;1,500;1,600;1,700;1,800&family=PT+Mono&display=swap"
  rel="stylesheet"
/>
```

Or use Fontsource:

```bash
npm install @fontsource/open-sans @fontsource/pt-mono
```

```javascript
// src/index.js
import "@fontsource/open-sans/300.css";
import "@fontsource/open-sans/400.css";
import "@fontsource/open-sans/500.css";
import "@fontsource/open-sans/600.css";
import "@fontsource/open-sans/700.css";
import "@fontsource/open-sans/800.css";
import "@fontsource/pt-mono";
```

### Basic Setup

```jsx
import { SaltProvider, Button } from "@salt-ds/core";
import "@salt-ds/theme/index.css";

function App() {
  return (
    <SaltProvider>
      <Button sentiment="accented" appearance="solid">
        Click Me
      </Button>
    </SaltProvider>
  );
}
```

## SaltProvider Configuration

Wrap your application in `SaltProvider` to enable theming, density, and mode:

```jsx
<SaltProvider
  mode="light"        // "light" | "dark"
  density="medium"    // "high" | "medium" | "low" | "touch"
  theme="salt-theme"  // theme class name
>
  {children}
</SaltProvider>
```

### Nested Providers

Create scoped theme/density sections:

```jsx
<SaltProvider mode="light" density="medium">
  <MainContent />
  <SaltProvider mode="dark" density="high">
    <DarkSidebar />
  </SaltProvider>
</SaltProvider>
```

### Access Theme with Hook

```jsx
import { useTheme } from "@salt-ds/core";

function MyComponent() {
  const { mode, density, theme } = useTheme();
  return <div>Current mode: {mode}</div>;
}
```

## Core Components

### Button

```jsx
import { Button } from "@salt-ds/core";

// Appearances: solid, bordered, transparent
// Sentiments: accented, neutral, positive, negative, caution

<Button sentiment="accented" appearance="solid">Primary</Button>
<Button sentiment="neutral" appearance="bordered">Secondary</Button>
<Button sentiment="negative" appearance="solid">Delete</Button>
<Button disabled>Disabled</Button>
```

### Input

```jsx
import { Input, FormField, FormFieldLabel, FormFieldHelperText } from "@salt-ds/core";

<FormField>
  <FormFieldLabel>Username</FormFieldLabel>
  <Input placeholder="Enter username" />
  <FormFieldHelperText>Must be unique</FormFieldHelperText>
</FormField>
```

### FormField Pattern

Always wrap form controls in `FormField` for accessibility:

```jsx
import {
  FormField,
  FormFieldLabel,
  FormFieldHelperText,
  Input,
  Checkbox,
  RadioButton,
  RadioButtonGroup,
} from "@salt-ds/core";

// Text Input
<FormField>
  <FormFieldLabel>Email</FormFieldLabel>
  <Input type="email" />
</FormField>

// With validation error
<FormField validationStatus="error">
  <FormFieldLabel>Password</FormFieldLabel>
  <Input type="password" />
  <FormFieldHelperText>Password is required</FormFieldHelperText>
</FormField>

// Checkbox
<FormField>
  <Checkbox label="I agree to terms" />
</FormField>

// Radio Group
<FormField>
  <FormFieldLabel>Payment Method</FormFieldLabel>
  <RadioButtonGroup>
    <RadioButton label="Credit Card" value="cc" />
    <RadioButton label="PayPal" value="paypal" />
  </RadioButtonGroup>
</FormField>
```

### Layout Components

```jsx
import {
  FlexLayout,
  StackLayout,
  GridLayout,
  FlowLayout,
  SplitLayout,
  BorderLayout,
} from "@salt-ds/core";

// Vertical stack
<StackLayout gap={2}>
  <Item1 />
  <Item2 />
</StackLayout>

// Horizontal flex
<FlexLayout gap={1} align="center">
  <Logo />
  <Navigation />
</FlexLayout>

// Grid
<GridLayout columns={3} gap={2}>
  <Card />
  <Card />
  <Card />
</GridLayout>
```

### Dialog

```jsx
import {
  Dialog,
  DialogHeader,
  DialogContent,
  DialogActions,
  DialogCloseButton,
  Button,
} from "@salt-ds/core";

function MyDialog({ open, onClose }) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogHeader header="Confirm Action" />
      <DialogCloseButton />
      <DialogContent>Are you sure you want to proceed?</DialogContent>
      <DialogActions>
        <Button appearance="bordered" onClick={onClose}>Cancel</Button>
        <Button sentiment="accented" appearance="solid">Confirm</Button>
      </DialogActions>
    </Dialog>
  );
}
```

### Menu

```jsx
import { Menu, MenuItem, MenuTrigger, MenuPanel, Button } from "@salt-ds/core";

<Menu>
  <MenuTrigger>
    <Button>Actions</Button>
  </MenuTrigger>
  <MenuPanel>
    <MenuItem onClick={() => {}}>Edit</MenuItem>
    <MenuItem onClick={() => {}}>Duplicate</MenuItem>
    <MenuItem onClick={() => {}}>Delete</MenuItem>
  </MenuPanel>
</Menu>
```

### Card

```jsx
import { Card, H3, Text } from "@salt-ds/core";

<Card>
  <H3>Card Title</H3>
  <Text>Card content goes here.</Text>
</Card>
```

### Pill

```jsx
import { Pill, PillGroup } from "@salt-ds/core";

// Single pill
<Pill>Label</Pill>

// Pill group for multi-selection
<PillGroup>
  <Pill value="one">Option 1</Pill>
  <Pill value="two">Option 2</Pill>
  <Pill value="three">Option 3</Pill>
</PillGroup>
```

## Icons

```jsx
import { AddIcon, DeleteIcon, EditIcon, SearchIcon } from "@salt-ds/icons";

<Button>
  <AddIcon /> Add Item
</Button>

// Icon sizes follow density by default
<SearchIcon size={1} /> // small
<SearchIcon size={2} /> // medium (default)
<SearchIcon size={3} /> // large
```

## Theming & Design Tokens

### Mode (Light/Dark)

```jsx
// At provider level
<SaltProvider mode="dark">

// Or toggle dynamically
const [mode, setMode] = useState("light");
<SaltProvider mode={mode}>
```

### Density System

Salt uses a 4px scaling grid with four densities:

- `high` - Compact, data-dense interfaces
- `medium` - Default, balanced spacing
- `low` - Spacious, consumer-facing
- `touch` - Touch-friendly, larger targets

```jsx
<SaltProvider density="high">
  <DataGrid /> {/* Compact data table */}
</SaltProvider>
```

### CSS Custom Properties

Salt uses CSS variables for theming. Override at any level:

```css
/* Foundation tokens */
--salt-spacing-100: 4px;
--salt-spacing-200: 8px;
--salt-spacing-300: 12px;

/* Palette tokens (mode-aware) */
--salt-palette-neutral-primary-foreground
--salt-palette-neutral-primary-background
--salt-palette-accent-foreground
--salt-palette-positive-foreground
--salt-palette-negative-foreground

/* Component tokens */
--salt-actionable-primary-background
--salt-actionable-primary-foreground
```

## Form Patterns

### Complete Form Example

```jsx
import {
  SaltProvider,
  FormField,
  FormFieldLabel,
  FormFieldHelperText,
  Input,
  Button,
  StackLayout,
  FlexLayout,
} from "@salt-ds/core";

function LoginForm() {
  return (
    <StackLayout gap={3}>
      <FormField>
        <FormFieldLabel>Email</FormFieldLabel>
        <Input type="email" />
      </FormField>
      
      <FormField>
        <FormFieldLabel>Password</FormFieldLabel>
        <Input type="password" />
        <FormFieldHelperText>Minimum 8 characters</FormFieldHelperText>
      </FormField>
      
      <FlexLayout gap={1} justify="end">
        <Button appearance="bordered">Cancel</Button>
        <Button sentiment="accented" appearance="solid">Sign In</Button>
      </FlexLayout>
    </StackLayout>
  );
}
```

### Validation States

```jsx
// Error state
<FormField validationStatus="error">
  <FormFieldLabel>Email</FormFieldLabel>
  <Input />
  <FormFieldHelperText>Invalid email format</FormFieldHelperText>
</FormField>

// Warning state
<FormField validationStatus="warning">
  <FormFieldLabel>Username</FormFieldLabel>
  <Input />
  <FormFieldHelperText>Username may already exist</FormFieldHelperText>
</FormField>

// Success state
<FormField validationStatus="success">
  <FormFieldLabel>Username</FormFieldLabel>
  <Input />
  <FormFieldHelperText>Username is available</FormFieldHelperText>
</FormField>
```

## Accessibility

Salt is WCAG 2.1 AA compliant. Key practices:

1. **Always use FormField** - Provides proper labeling and ARIA attributes
1. **Semantic HTML** - Components render appropriate HTML elements
1. **Keyboard navigation** - All interactive components are keyboard accessible
1. **Focus management** - Proper focus indicators and trap management in modals
1. **Screen reader support** - Tested with NVDA (Firefox), JAWS (Chrome), VoiceOver (Safari)

```jsx
// ✅ Good - proper form structure
<FormField>
  <FormFieldLabel>Name</FormFieldLabel>
  <Input aria-describedby="name-hint" />
  <FormFieldHelperText id="name-hint">Enter your full name</FormFieldHelperText>
</FormField>

// ❌ Avoid - missing label association
<label>Name</label>
<Input />
```

## Lab Components

Experimental components in `@salt-ds/lab` (use with caution):

```jsx
import { ComboBox, Dropdown, DatePicker } from "@salt-ds/lab";

// These may have breaking changes
<ComboBox source={options} />
```

## Component Reference

See <references/components.md> for the full component list and API details.

## Additional Resources

- Documentation: https://www.saltdesignsystem.com
- GitHub: https://github.com/jpmorganchase/salt-ds
- Storybook: Available in the repo for component examples

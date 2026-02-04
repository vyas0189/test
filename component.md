# Salt Design System - Component Reference

Complete list of components available in Salt Design System packages.

## Table of Contents

1. [Core Components (@salt-ds/core)](#core-components)
1. [Lab Components (@salt-ds/lab)](#lab-components)
1. [Icons (@salt-ds/icons)](#icons)
1. [Common Props](#common-props)

-----

## Core Components

### Actions

|Component          |Description                                                          |Import         |
|-------------------|---------------------------------------------------------------------|---------------|
|`Button`           |Interactive action button with solid/bordered/transparent appearances|`@salt-ds/core`|
|`ToggleButton`     |Button that toggles between two states                               |`@salt-ds/core`|
|`ToggleButtonGroup`|Group of toggle buttons                                              |`@salt-ds/core`|
|`Link`             |Navigation link component                                            |`@salt-ds/core`|

### Button Props

```typescript
interface ButtonProps {
  appearance?: "solid" | "bordered" | "transparent";
  sentiment?: "accented" | "neutral" | "positive" | "negative" | "caution";
  disabled?: boolean;
  focusableWhenDisabled?: boolean;
  type?: "button" | "submit" | "reset";
}
```

### Data Display

|Component          |Description                       |Import         |
|-------------------|----------------------------------|---------------|
|`Avatar`           |User avatar with image or initials|`@salt-ds/core`|
|`Badge`            |Notification badge indicator      |`@salt-ds/core`|
|`Card`             |Container for grouped content     |`@salt-ds/core`|
|`InteractableCard` |Clickable card variant            |`@salt-ds/core`|
|`Pill`             |Compact label/tag element         |`@salt-ds/core`|
|`PillGroup`        |Multi-selection pill group        |`@salt-ds/core`|
|`Tag`              |Categorization label              |`@salt-ds/core`|
|`StatusIndicator`  |Visual status indicator           |`@salt-ds/core`|
|`Text`             |Typography component for body text|`@salt-ds/core`|
|`H1-H6`            |Heading components                |`@salt-ds/core`|
|`Display1-Display4`|Large display text                |`@salt-ds/core`|
|`Label`            |Label text component              |`@salt-ds/core`|

### Form Controls

|Component            |Description                                |Import         |
|---------------------|-------------------------------------------|---------------|
|`FormField`          |Wrapper for form controls with label/helper|`@salt-ds/core`|
|`FormFieldLabel`     |Label for form field                       |`@salt-ds/core`|
|`FormFieldHelperText`|Helper/error text for form field           |`@salt-ds/core`|
|`Input`              |Single-line text input                     |`@salt-ds/core`|
|`MultilineInput`     |Multi-line textarea                        |`@salt-ds/core`|
|`Checkbox`           |Checkbox control                           |`@salt-ds/core`|
|`CheckboxGroup`      |Group of checkboxes                        |`@salt-ds/core`|
|`RadioButton`        |Radio button control                       |`@salt-ds/core`|
|`RadioButtonGroup`   |Group of radio buttons                     |`@salt-ds/core`|
|`Switch`             |Toggle switch control                      |`@salt-ds/core`|
|`Slider`             |Range slider input                         |`@salt-ds/core`|
|`NumberInput`        |Numeric input with stepper                 |`@salt-ds/core`|

### FormField Props

```typescript
interface FormFieldProps {
  disabled?: boolean;
  readOnly?: boolean;
  necessity?: "required" | "optional" | "asterisk";
  validationStatus?: "error" | "warning" | "success";
  labelPlacement?: "top" | "left" | "right";
}
```

### Input Props

```typescript
interface InputProps {
  value?: string;
  defaultValue?: string;
  onChange?: (event: ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  disabled?: boolean;
  readOnly?: boolean;
  startAdornment?: ReactNode;
  endAdornment?: ReactNode;
  textAlign?: "left" | "center" | "right";
  variant?: "primary" | "secondary";
}
```

### Layout

|Component          |Description                 |Import         |
|-------------------|----------------------------|---------------|
|`FlexLayout`       |Flexbox-based layout        |`@salt-ds/core`|
|`StackLayout`      |Vertical/horizontal stack   |`@salt-ds/core`|
|`GridLayout`       |CSS Grid layout             |`@salt-ds/core`|
|`FlowLayout`       |Wrap-based layout           |`@salt-ds/core`|
|`SplitLayout`      |Two-pane split layout       |`@salt-ds/core`|
|`BorderLayout`     |Header/footer/sidebar layout|`@salt-ds/core`|
|`ParentChildLayout`|Master-detail layout        |`@salt-ds/core`|

### Layout Props

```typescript
interface StackLayoutProps {
  direction?: "row" | "column";
  gap?: 0 | 1 | 2 | 3 | 4 | 5 | 6;  // Multiplier of base spacing
  align?: "start" | "center" | "end" | "stretch" | "baseline";
  separators?: boolean | "start" | "center" | "end";
}

interface FlexLayoutProps {
  direction?: "row" | "column" | "row-reverse" | "column-reverse";
  wrap?: boolean | "wrap" | "nowrap" | "wrap-reverse";
  gap?: number;
  align?: "start" | "center" | "end" | "stretch" | "baseline";
  justify?: "start" | "center" | "end" | "space-between" | "space-around" | "space-evenly";
}

interface GridLayoutProps {
  columns?: number | string;
  rows?: number | string;
  gap?: number;
  columnGap?: number;
  rowGap?: number;
}
```

### Navigation

|Component       |Description               |Import         |
|----------------|--------------------------|---------------|
|`NavigationItem`|Nav item within navigation|`@salt-ds/core`|
|`TabBar`        |Horizontal tab navigation |`@salt-ds/core`|
|`Tabs`          |Tab panel container       |`@salt-ds/core`|
|`TabPanel`      |Content panel for tab     |`@salt-ds/core`|
|`Breadcrumbs`   |Breadcrumb navigation     |`@salt-ds/core`|
|`Pagination`    |Page navigation           |`@salt-ds/core`|

### Overlays

|Component          |Description             |Import         |
|-------------------|------------------------|---------------|
|`Dialog`           |Modal dialog container  |`@salt-ds/core`|
|`DialogHeader`     |Dialog header with title|`@salt-ds/core`|
|`DialogContent`    |Dialog body content     |`@salt-ds/core`|
|`DialogActions`    |Dialog action buttons   |`@salt-ds/core`|
|`DialogCloseButton`|Dialog close button     |`@salt-ds/core`|
|`Drawer`           |Side panel drawer       |`@salt-ds/core`|
|`Menu`             |Dropdown menu           |`@salt-ds/core`|
|`MenuItem`         |Menu item               |`@salt-ds/core`|
|`MenuTrigger`      |Menu trigger element    |`@salt-ds/core`|
|`MenuPanel`        |Menu content panel      |`@salt-ds/core`|
|`Tooltip`          |Hover tooltip           |`@salt-ds/core`|
|`Toast`            |Notification toast      |`@salt-ds/core`|
|`ToastContent`     |Toast message content   |`@salt-ds/core`|
|`Overlay`          |Base overlay component  |`@salt-ds/core`|

### Dialog Props

```typescript
interface DialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  size?: "small" | "medium" | "large";
  status?: "info" | "success" | "warning" | "error";
}
```

### Feedback & Status

|Component         |Description                   |Import         |
|------------------|------------------------------|---------------|
|`Banner`          |Full-width notification banner|`@salt-ds/core`|
|`Spinner`         |Loading spinner               |`@salt-ds/core`|
|`LinearProgress`  |Linear progress bar           |`@salt-ds/core`|
|`CircularProgress`|Circular progress indicator   |`@salt-ds/core`|

### Providers

|Component         |Description                     |Import         |
|------------------|--------------------------------|---------------|
|`SaltProvider`    |Theme/mode/density provider     |`@salt-ds/core`|
|`SaltProviderNext`|Extended provider with JPM Brand|`@salt-ds/core`|

### SaltProvider Props

```typescript
interface SaltProviderProps {
  mode?: "light" | "dark";
  density?: "high" | "medium" | "low" | "touch";
  theme?: string;
  children: ReactNode;
}
```

### Utilities

|Component       |Description               |Import         |
|----------------|--------------------------|---------------|
|`Scrim`         |Background overlay        |`@salt-ds/core`|
|`Separator`     |Visual divider            |`@salt-ds/core`|
|`Panel`         |Container with background |`@salt-ds/core`|
|`VisuallyHidden`|Screen-reader only content|`@salt-ds/core`|

-----

## Lab Components

Components in `@salt-ds/lab` are experimental and may have breaking changes.

|Component       |Description                     |Status|
|----------------|--------------------------------|------|
|`ComboBox`      |Autocomplete input with dropdown|RC    |
|`Dropdown`      |Select dropdown                 |RC    |
|`DatePicker`    |Date selection                  |RC    |
|`Calendar`      |Calendar view                   |RC    |
|`TokenizedInput`|Multi-value input with pills    |RC    |
|`FileDropZone`  |File upload drop area           |RC    |
|`Tree`          |Tree view component             |RC    |
|`DataGrid`      |Data table grid                 |Beta  |
|`AgGrid`        |AG Grid integration             |Beta  |

-----

## Icons

Import icons from `@salt-ds/icons`. Icons scale with density automatically.

### Common Icons

```jsx
import {
  // Actions
  AddIcon,
  DeleteIcon,
  EditIcon,
  SaveIcon,
  CloseIcon,
  RefreshIcon,
  
  // Navigation
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  HomeIcon,
  MenuIcon,
  
  // Status
  ErrorIcon,
  WarningIcon,
  SuccessIcon,
  InfoIcon,
  
  // Common
  SearchIcon,
  SettingsIcon,
  UserIcon,
  FilterIcon,
  SortIcon,
  DownloadIcon,
  UploadIcon,
  CopyIcon,
  PrintIcon,
} from "@salt-ds/icons";
```

### Icon Props

```typescript
interface IconProps {
  size?: 1 | 2 | 3;  // Small, Medium, Large
  className?: string;
  style?: CSSProperties;
}
```

-----

## Common Props

Most Salt components share these common props:

```typescript
interface CommonProps {
  className?: string;
  style?: CSSProperties;
  id?: string;
  "data-testid"?: string;
}

// For interactive components
interface InteractiveProps extends CommonProps {
  disabled?: boolean;
  "aria-label"?: string;
  "aria-describedby"?: string;
}
```

## Hooks

|Hook           |Description                      |Import         |
|---------------|---------------------------------|---------------|
|`useTheme`     |Access current theme/mode/density|`@salt-ds/core`|
|`useDensity`   |Access current density value     |`@salt-ds/core`|
|`useId`        |Generate unique IDs              |`@salt-ds/core`|
|`useControlled`|Controlled/uncontrolled state    |`@salt-ds/core`|
|`useForkRef`   |Merge refs                       |`@salt-ds/core`|

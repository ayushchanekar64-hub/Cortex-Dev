# Sandpack Live Preview Integration

## Overview
Successfully integrated @codesandbox/sandpack-react for live React code preview in the Auto Dev Agent project.

## Implementation Details

### 1. SandpackPreview Component
- **Location**: `frontend/components/SandpackPreview.tsx`
- **Features**:
  - Dynamic file injection from generated code
  - React app detection (checks for App.js, App.jsx, App.tsx, index.js, or React imports)
  - Loading state with animated spinner
  - Error handling with retry functionality
  - Dark theme matching dashboard design
  - Refresh button to reload preview

### 2. Updated LivePreview Component
- **Location**: `frontend/components/LivePreview.tsx`
- **Changes**:
  - Integrated SandpackPreview for React apps
  - Toggle between code view and live preview
  - Maintains file editing capabilities
  - React app detection logic
  - Dark theme styling

### 3. Split Screen Layout
- **Location**: `frontend/pages/index.tsx`
- **Layout**:
  - **Left**: File Explorer (256px width)
  - **Center**: Code Editor (flexible width)
  - **Right**: Live Preview (flexible width)
- Removed tab-based navigation for simultaneous view
- Added Monitor icon import

## Example Usage

### React App Example
When the AI generates a React app, it will automatically render in the live preview:

```javascript
// Example generated App.js
import React from 'react';

function App() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>Hello from Sandpack!</h1>
      <p>This is a live preview of your React code.</p>
      <button onClick={() => alert('Clicked!')}>
        Click Me
      </button>
    </div>
  );
}

export default App;
```

### Supported File Types
- React components (.js, .jsx, .tsx)
- CSS files (.css)
- JSON configuration files
- Any frontend files (excludes backend .py files)

## Features

### Loading State
- Animated spinner while preview prepares
- Status indicator in header (Loading/Ready)
- Smooth transitions

### Error Handling
- Error overlay with retry button
- Clear error messages
- Graceful fallback to code view

### Dark Theme
- Matches dashboard aesthetic
- Indigo accent colors
- Consistent spacing and borders
- Custom scrollbars

### Dynamic File Injection
- Automatically converts generated files to Sandpack format
- Normalizes file paths
- Handles nested directory structures
- Ensures App.js exists for Sandpack

## Constraints
- **Only supports React apps** for live preview
- Backend files (.py) are excluded
- Non-React apps show file list view with message

## Testing
1. Start the dev server: `npm run dev`
2. Generate a React app using the AI
3. View the split screen layout
4. See live preview in the right panel
5. Toggle between code and preview using the button in LivePreview header

## Dependencies
- @codesandbox/sandpack-react: ^2.20.0 (already installed)
- React: ^18.2.0
- Framer Motion: ^10.16.0
- Lucide React: ^0.292.0

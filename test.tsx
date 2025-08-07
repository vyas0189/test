import React, { useCallback, useMemo } from ‘react’;
import { createEditor, Transforms, Editor, Text, Node } from ‘slate’;
import { Slate, Editable, withReact } from ‘slate-react’;
import { Controller } from ‘react-hook-form’;

const CustomTextArea = ({ name, control, rows = 5, rules = {}, …props }) => {
// Create a Slate editor object that won’t change across renders
const editor = useMemo(() => withReact(createEditor()), []);

// Initialize empty value
const initialValue = [
{
type: ‘paragraph’,
children: [{ text: ‘’ }],
},
];

// Helper function to serialize Slate value to plain text
const serialize = (value) => {
return value
.map(n => Node.string(n))
.join(’\n’);
};

// Helper function to deserialize plain text to Slate value
const deserialize = (text) => {
if (!text) return initialValue;

```
const lines = text.split('\n');
return lines.map(line => ({
  type: 'paragraph',
  children: [{ text: line }],
}));
```

};

// Custom renderElement function
const renderElement = useCallback((props) => {
switch (props.element.type) {
default:
return <p {…props.attributes}>{props.children}</p>;
}
}, []);

// Custom renderLeaf function
const renderLeaf = useCallback((props) => {
return <span {…props.attributes}>{props.children}</span>;
}, []);

// Handle key events for basic functionality
const handleKeyDown = useCallback((event) => {
if (event.key === ‘Enter’) {
event.preventDefault();
Transforms.insertText(editor, ‘\n’);
}
}, [editor]);

return (
<Controller
name={name}
control={control}
rules={rules}
defaultValue=””
render={({ field: { onChange, value } }) => {
// Convert string value to Slate value
const slateValue = useMemo(() => deserialize(value), [value]);

```
    return (
      <Slate
        editor={editor}
        initialValue={slateValue}
        onChange={(newValue) => {
          // Only update if the document content has changed
          const isAstChange = editor.operations.some(
            op => 'set_selection' !== op.type
          );
          
          if (isAstChange) {
            // Convert Slate value back to plain text
            const text = serialize(newValue);
            onChange(text);
          }
        }}
      >
        <Editable
          className="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 resize-none"
          style={{ 
            minHeight: `${rows * 1.5}rem`,
            outline: 'none'
          }}
          renderElement={renderElement}
          renderLeaf={renderLeaf}
          onKeyDown={handleKeyDown}
          placeholder="Enter text..."
          {...props}
        />
      </Slate>
    );
  }}
/>
```

);
};

export default CustomTextArea;

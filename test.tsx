// ProductsGrid.jsx
import { useState, useMemo, useCallback, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import Select from 'react-select';
import { useProductsQuery, useSubmitMutation } from './api';
import {
  StatusCellRenderer,
  CommentsCellRenderer,
  SubmitButtonCellRenderer,
} from './cellRenderers';

const ProductsGrid = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [selectedTags, setSelectedTags] = useState(['New']);
  const [submittedAppIds, setSubmittedAppIds] = useState([]);
  const [rowData, setRowData] = useState([]);
  
  // Toggle dark mode class on body
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const { isLoading } = useProductsQuery(selectedTags, {
    onSuccess: (data) => setRowData(data),
  });
  
  const mutation = useSubmitMutation();

  // Custom styles for react-select with dark mode
  const selectStyles = useMemo(() => ({
    control: (base) => ({
      ...base,
      backgroundColor: isDarkMode ? '#1f2937' : '#fff',
      borderColor: isDarkMode ? '#374151' : '#d1d5db',
      color: isDarkMode ? '#fff' : '#111827',
    }),
    menu: (base) => ({
      ...base,
      backgroundColor: isDarkMode ? '#1f2937' : '#fff',
    }),
    option: (base, state) => ({
      ...base,
      backgroundColor: state.isFocused 
        ? (isDarkMode ? '#374151' : '#f3f4f6')
        : 'transparent',
      color: isDarkMode ? '#fff' : '#111827',
    }),
    multiValue: (base) => ({
      ...base,
      backgroundColor: isDarkMode ? '#374151' : '#e5e7eb',
    }),
    multiValueLabel: (base) => ({
      ...base,
      color: isDarkMode ? '#fff' : '#111827',
    }),
  }), [isDarkMode]);

  // Modified cell renderers with Tailwind classes
  const StatusCellRenderer = (params) => {
    const isSubmitted = params.context.submittedAppIds.includes(params.data.appId);
    
    return (
      <select
        className="w-full bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-2 py-1 rounded border border-gray-300 dark:border-gray-600"
        value={params.value}
        onChange={(e) => params.context.updateRowData(params.node.id, 'status', e.target.value)}
        disabled={isSubmitted}
      >
        <option value="Approved">Approved</option>
        <option value="Denied">Denied</option>
        <option value="Need More Info">Need More Info</option>
      </select>
    );
  };

  const CommentsCellRenderer = (params) => {
    const isSubmitted = params.context.submittedAppIds.includes(params.data.appId);
    
    return (
      <textarea
        className="w-full h-full bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-2 py-1 rounded border border-gray-300 dark:border-gray-600 resize-none"
        value={params.value || ''}
        onChange={(e) => params.context.updateRowData(params.node.id, 'comments', e.target.value)}
        disabled={isSubmitted}
      />
    );
  };

  const SubmitButtonCellRenderer = (params) => {
    const isSubmitted = params.context.submittedAppIds.includes(params.data.appId);
    const handleSubmit = () => {
      params.context.handleSubmit(params.data);
    };

    return (
      <button
        className={`px-4 py-2 rounded ${
          isSubmitted 
            ? 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 text-white'
        } transition-colors`}
        onClick={handleSubmit}
        disabled={isSubmitted}
      >
        Submit
      </button>
    );
  };

  // Rest of the component remains similar with Tailwind classes added
  return (
    <div className="h-screen flex flex-col dark:bg-gray-900">
      <div className="p-4 flex justify-between items-center bg-gray-100 dark:bg-gray-800">
        <Select
          isMulti
          styles={selectStyles}
          options={[
            { value: 'Approved', label: 'Approved' },
            { value: 'Denied', label: 'Denied' },
            { value: 'New', label: 'New' },
            { value: 'Need More Info', label: 'Need More Info' },
          ]}
          value={selectedTags.map(tag => ({ value: tag, label: tag }))}
          onChange={selected => setSelectedTags(selected.map(opt => opt.value))}
          className="w-96"
        />
        
        <button
          onClick={() => setIsDarkMode(!isDarkMode)}
          className="px-4 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          {isDarkMode ? '🌙 Dark' : '☀️ Light'}
        </button>
      </div>

      <div className={`flex-1 px-4 pb-4 ${isDarkMode ? 'ag-theme-alpine-dark' : 'ag-theme-alpine'}`}>
        <AgGridReact
          rowData={rowData}
          columnDefs={columnDefs}
          context={gridContext}
          onGridReady={(params) => params.api.sizeColumnsToFit()}
          className="w-full h-full rounded-lg shadow-lg overflow-hidden"
        />
      </div>
    </div>
  );
};

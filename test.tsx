// StatusCellRenderer.jsx
const StatusCellRenderer = (params) => {
  const isSubmitted = params.context.submittedAppIds.includes(params.data.appId);
  
  return (
    <select
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

// CommentsCellRenderer.jsx
const CommentsCellRenderer = (params) => {
  const isSubmitted = params.context.submittedAppIds.includes(params.data.appId);
  
  return (
    <textarea
      value={params.value || ''}
      onChange={(e) => params.context.updateRowData(params.node.id, 'comments', e.target.value)}
      disabled={isSubmitted}
    />
  );
};

// SubmitButtonCellRenderer.jsx
const SubmitButtonCellRenderer = (params) => {
  const isSubmitted = params.context.submittedAppIds.includes(params.data.appId);
  const handleSubmit = () => {
    params.context.handleSubmit(params.data);
  };

  return (
    <button onClick={handleSubmit} disabled={isSubmitted}>
      Submit
    </button>
  );
};



// ProductsGrid.jsx
import { useState, useMemo, useCallback } from 'react';
import { AgGridReact } from 'ag-grid-react';
import Select from 'react-select';
import { useProductsQuery, useSubmitMutation } from './api';
import {
  StatusCellRenderer,
  CommentsCellRenderer,
  SubmitButtonCellRenderer,
} from './cellRenderers';

const ProductsGrid = () => {
  const [selectedTags, setSelectedTags] = useState(['New']);
  const [submittedAppIds, setSubmittedAppIds] = useState([]);
  const [rowData, setRowData] = useState([]);
  
  const { isLoading } = useProductsQuery(selectedTags, {
    onSuccess: (data) => setRowData(data),
  });
  
  const mutation = useSubmitMutation();

  const updateRowData = useCallback((rowId, field, value) => {
    setRowData(prev => prev.map(row => 
      row.id === rowId ? { ...row, [field]: value } : row
    ));
  }, []);

  const handleSubmit = useCallback((rowData) => {
    mutation.mutate(rowData, {
      onSuccess: () => {
        setSubmittedAppIds(prev => [...prev, rowData.appId]);
      },
    });
  }, [mutation]);

  const columnDefs = useMemo(() => [
    { field: 'appId', headerName: 'App ID' },
    // ... other columns
    { 
      field: 'status', 
      cellRenderer: StatusCellRenderer,
      cellRendererParams: { context: {} } // Will be overridden
    },
    { field: 'comments', cellRenderer: CommentsCellRenderer },
    { cellRenderer: SubmitButtonCellRenderer },
  ], []);

  const gridContext = useMemo(() => ({
    submittedAppIds,
    updateRowData,
    handleSubmit,
  }), [submittedAppIds, updateRowData, handleSubmit]);

  return (
    <div className="ag-theme-alpine" style={{ height: 500 }}>
      <Select
        isMulti
        options={[
          { value: 'Approved', label: 'Approved' },
          { value: 'Denied', label: 'Denied' },
          { value: 'New', label: 'New' },
          { value: 'Need More Info', label: 'Need More Info' },
        ]}
        value={selectedTags.map(tag => ({ value: tag, label: tag }))}
        onChange={selected => setSelectedTags(selected.map(opt => opt.value))}
      />
      
      <AgGridReact
        rowData={rowData}
        columnDefs={columnDefs}
        context={gridContext}
        onGridReady={(params) => params.api.sizeColumnsToFit()}
      />
    </div>
  );
};

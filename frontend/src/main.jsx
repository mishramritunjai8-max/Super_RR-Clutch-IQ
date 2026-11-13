import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Global Error Boundary to prevent "black screen" on any uncaught React exception
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('SUPER RR CLUTCH IQ - Caught React Render Error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          backgroundColor: '#1C1D20',
          color: '#F2F4F1',
          padding: '40px 20px',
          fontFamily: "'Archivo', system-ui, sans-serif",
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center'
        }}>
          <div style={{
            maxWidth: '600px',
            backgroundColor: '#25262A',
            border: '1px solid #FFC928',
            borderRadius: '16px',
            padding: '32px',
            boxShadow: '0 0 25px rgba(255, 201, 40, 0.2)'
          }}>
            <div style={{ fontSize: '32px', marginBottom: '12px' }}>⚠️</div>
            <h1 style={{ color: '#FFC928', fontSize: '22px', fontWeight: 'bold', margin: '0 0 12px 0' }}>
              Application Render Notice
            </h1>
            <p style={{ color: '#F2F4F1', fontSize: '15px', lineHeight: '1.5', margin: '0 0 16px 0' }}>
              {this.state.error?.message || String(this.state.error)}
            </p>
            {this.state.errorInfo && (
              <pre style={{
                textAlign: 'left',
                backgroundColor: '#141517',
                color: '#A6A9A5',
                padding: '12px',
                borderRadius: '8px',
                fontSize: '11px',
                overflowX: 'auto',
                maxHeight: '180px'
              }}>
                {this.state.errorInfo.componentStack}
              </pre>
            )}
            <div style={{ marginTop: '20px', display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button
                onClick={() => window.location.reload()}
                style={{
                  backgroundColor: '#FFC928',
                  color: '#1C1D20',
                  fontWeight: 'bold',
                  padding: '10px 20px',
                  borderRadius: '10px',
                  border: 'none',
                  cursor: 'pointer'
                }}
              >
                Reload Page
              </button>
              <button
                onClick={() => window.location.href = '/'}
                style={{
                  backgroundColor: 'transparent',
                  color: '#F2F4F1',
                  border: '1px solid rgba(242, 244, 241, 0.2)',
                  padding: '10px 20px',
                  borderRadius: '10px',
                  cursor: 'pointer'
                }}
              >
                Return to Home
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

// Window unhandled error trap
window.addEventListener('error', (event) => {
  console.error('Global script error:', event.error || event.message);
});

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Failed to find root element to mount application.');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);

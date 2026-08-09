import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import EssayDisplay from './EssayDisplay';
import Button from './ui/Button';
import Card from './ui/Card';
import ConfirmModal from './ui/ConfirmModal';

function EssayDetail() {
  const { id } = useParams();
  const { getToken } = useAuth();
  const navigate = useNavigate();
  const [essayData, setEssayData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteModal, setDeleteModal] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchEssay();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const fetchEssay = async () => {
    try {
      const token = await getToken();
      const backendUrl = import.meta.env.VITE_BACKEND;
      
      const response = await fetch(`${backendUrl}/essays/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.status === 404) {
        setError('Essay not found');
        setLoading(false);
        return;
      }
      
      if (!response.ok) {
        throw new Error('Failed to fetch essay');
      }
      
      const data = await response.json();
      const rawFeedback = data.essay?.feedback;
      const parsedFeedback = typeof rawFeedback === 'string'
        ? JSON.parse(rawFeedback)
        : rawFeedback;
      setEssayData(parsedFeedback);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching essay:', err);
      setError('Failed to load essay feedback');
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      const token = await getToken();
      const backendUrl = import.meta.env.VITE_BACKEND;
      
      const response = await fetch(`${backendUrl}/essays/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        navigate('/dashboard');
      } else {
        throw new Error('Failed to delete');
      }
    } catch (err) {
      console.error('Delete error:', err);
      alert('Failed to delete. Please try again.');
    } finally {
      setDeleting(false);
      setDeleteModal(false);
    }
  };

  if (error) {
    return (
      <div className="bg-white min-h-screen">
        <section className="section">
          <div className="container max-w-3xl">
            <Card variant="elevated" padding="lg">
              <div className="text-center py-8">
                <svg className="w-16 h-16 mx-auto text-red-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <h2 className="text-2xl font-bold text-[var(--color-text-primary)] mb-2">
                  {error}
                </h2>
                <p className="text-[var(--color-text-secondary)] mb-6">
                  This essay might have been deleted or doesn't exist.
                </p>
                <Button variant="primary" onClick={() => navigate('/dashboard')}>
                  ← Back to Dashboard
                </Button>
              </div>
            </Card>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="bg-white min-h-screen">
      <section className="section">
        <div className="container">
          <div className="mb-6 flex justify-between items-center">
            <Button variant="outline" onClick={() => navigate('/dashboard')}>
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Dashboard
            </Button>
            <Button 
              variant="outline" 
              onClick={() => setDeleteModal(true)}
              className="text-red-600 hover:bg-red-50 border-red-200"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Delete Essay
            </Button>
          </div>
          <EssayDisplay essay={essayData} loading={loading} />
        </div>
      </section>

      {/* Confirmation Modal */}
      <ConfirmModal
        isOpen={deleteModal}
        onClose={() => setDeleteModal(false)}
        onConfirm={handleDelete}
        title="Delete this essay?"
        message="This action cannot be undone. The essay feedback will be permanently deleted from your account."
        confirmText="Delete"
        loading={deleting}
      />
    </div>
  );
}

export default EssayDetail;


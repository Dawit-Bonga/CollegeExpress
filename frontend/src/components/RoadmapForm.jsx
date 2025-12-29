import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import Button from './ui/Button';
import Card from './ui/Card';
import { Input, Textarea, Select } from './ui/Input';

function RoadmapForm({ setRoadmap, setLoading }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [gpa, setGpa] = useState('');
  const [grade, setGrade] = useState('');
  const [interests, setInterests] = useState('');
  const [activities, setActivities] = useState('');
  const [demographic, setDemographic] = useState('');
  const [testing, setTesting] = useState('');
  const [location, setLocation] = useState('');
  const [collegeGoals, setCollegeGoals] = useState(''); 
  const [classes, setClasses] = useState('');
  const [error, setError] = useState('');
  const [retryCount, setRetryCount] = useState(0);
  const { getToken } = useAuth();

  const steps = [
    {
      title: "Grade Level",
      description: "Let's start with the basics",
      fields: ['grade']
    },
    {
      title: "Academic Performance",
      description: "Tell us about your GPA and courses",
      fields: ['gpa', 'classes']
    },
    {
      title: "Interests & Goals",
      description: "What are you passionate about?",
      fields: ['interests']
    },
    {
      title: "Activities",
      description: "Share your extracurriculars",
      fields: ['activities']
    },
    {
      title: "Testing & Demographics",
      description: "Help us understand your background",
      fields: ['testing', 'demographic']
    },
    {
      title: "College Preferences",
      description: "What are you looking for in a college?",
      fields: ['collegeGoals', 'location']
    }
  ];

  const validateStep = () => {
    const currentFields = steps[currentStep].fields;
    const fieldValues = { grade, gpa, classes, interests, activities, testing, demographic, collegeGoals, location };
    
    for (const field of currentFields) {
      const value = fieldValues[field];
      // Skip optional fields (demographic)
      if (field === 'demographic') continue;
      
      if (!value || value.trim() === '') {
        return false;
      }
    }
    return true;
  };

  const handleNext = () => {
    if (validateStep()) {
      setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateStep()) {
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const token = await getToken();
      const response = await fetch(`${import.meta.env.VITE_BACKEND}/generate`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ gpa, grade, interests, activities, demographic, testing, collegeGoals, classes, location })
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.roadmap) {
        throw new Error('No roadmap data received from server');
      }
      
      setRoadmap(data.roadmap);
      setRetryCount(0);
    } catch (err) {
      console.error('Roadmap generation error:', err);
      
      let errorMessage = 'Failed to generate roadmap. ';
      
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        errorMessage += 'Unable to connect to the server. Please check your internet connection.';
      } else if (err.message.includes('Server error: 500')) {
        errorMessage += 'Server is temporarily unavailable. Please try again later.';
      } else if (err.message.includes('Server error: 400')) {
        errorMessage += 'Invalid input data. Please check your form entries.';
      } else if (err.message.includes('Server error: 429')) {
        errorMessage += 'Too many requests. Please wait a moment before trying again.';
      } else {
        errorMessage += err.message || 'An unexpected error occurred.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    setError('');
    handleSubmit(new Event('submit'));
  };

  const renderStepContent = () => {
    switch(currentStep) {
      case 0:
        return (
          <Select
            label="Grade Level"
            value={grade}
            onChange={(e) => setGrade(e.target.value)}
            required
            helperText="Your current academic year"
          >
            <option value="">Select your grade</option>
            <option value="9">9th Grade</option>
            <option value="10">10th Grade</option>
            <option value="11">11th Grade</option>
            <option value="12">12th Grade</option>
            <option value="Community college">Community College</option>
            <option value="other">Out of school, looking to get back in</option>
          </Select>
        );
      
      case 1:
        return (
          <>
            <Input
              label="GPA"
              type="number"
              value={gpa}
              onChange={(e) => setGpa(e.target.value)}
              step="0.01"
              min="0"
              max="4"
              placeholder="e.g., 3.5"
              helperText="Your current grade point average (0.0-4.0 scale)"
              required
            />
            <Textarea
              label="Course Rigor"
              value={classes}
              onChange={(e) => setClasses(e.target.value)}
              placeholder="e.g., I have taken 7/11 AP classes, We have no AP or Honors Classes. Also feel free to drop your upcoming schedule"
              helperText="Describe the difficulty of your classes and any advanced courses"
              rows={4}
              required
            />
          </>
        );
      
      case 2:
        return (
          <Textarea
            label="Interests & Goals"
            value={interests}
            onChange={(e) => setInterests(e.target.value)}
            placeholder="e.g., computer science, medicine, social justice"
            helperText="What are you passionate about? What do you want to study?"
            rows={4}
            required
          />
        );
      
      case 3:
        return (
          <Textarea
            label="Activities & Extracurriculars"
            value={activities}
            onChange={(e) => setActivities(e.target.value)}
            placeholder="e.g., debate, HackClub, Research - please try to be specific"
            helperText="List your clubs, sports, volunteer work, jobs, etc."
            rows={4}
            required
          />
        );
      
      case 4:
        return (
          <>
            <Textarea
              label="SAT/Testing"
              value={testing}
              onChange={(e) => setTesting(e.target.value)}
              placeholder="e.g., 1330 SAT, haven't taken the SAT yet, plan on taking it soon aiming for..."
              helperText="Current scores or testing plans (SAT, ACT, AP exams, etc.)"
              rows={3}
            />
            <Textarea
              label="Demographic Information"
              value={demographic}
              onChange={(e) => setDemographic(e.target.value)}
              placeholder="e.g., first-generation college student, low-income, rural area, underrepresented minority"
              helperText="Optional: Help us tailor advice to your unique circumstances"
              rows={3}
            />
          </>
        );
      
      case 5:
        return (
          <>
            <Textarea
              label="College Goals"
              value={collegeGoals}
              onChange={(e) => setCollegeGoals(e.target.value)}
              placeholder="e.g., Ivy League, state schools, specific universities, community college transfer, gap year plans"
              helperText="What type of colleges are you interested in?"
              rows={3}
            />
            <Textarea
              label="Location Preferences"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., want to stay close to home in California, open to East Coast, prefer urban areas, must be near family"
              helperText="Geographic preferences or constraints for college location"
              rows={3}
            />
          </>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      {error && (
        <Card variant="default" padding="default" className="mb-6 bg-red-50 border-red-200">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-red-800 mb-1">Error generating roadmap</h4>
              <p className="text-sm text-red-700 mb-3">{error}</p>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRetry}
                  disabled={retryCount >= 3}
                  className="border-red-300 text-red-700 hover:bg-red-100"
                >
                  {retryCount >= 3 ? 'Max retries reached' : `Retry (${retryCount}/3)`}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setError('')}
                  className="text-red-700 hover:bg-red-100"
                >
                  Dismiss
                </Button>
              </div>
            </div>
          </div>
        </Card>
      )}
      
      <Card variant="elevated" padding="lg">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-[var(--color-text-secondary)]">
              Step {currentStep + 1} of {steps.length}
            </span>
            <span className="text-sm font-medium text-[var(--color-text-secondary)]">
              {Math.round(((currentStep + 1) / steps.length) * 100)}% Complete
            </span>
          </div>
          <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-[var(--color-accent)] transition-all duration-300 ease-in-out rounded-full"
              style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-[var(--color-text-primary)] mb-2">
            {steps[currentStep].title}
          </h2>
          <p className="text-[var(--color-text-secondary)]">
            {steps[currentStep].description}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="min-h-[200px]">
            {renderStepContent()}
          </div>

          {/* Navigation Buttons */}
          <div className="pt-4 flex gap-3">
            {currentStep > 0 && (
              <Button
                type="button"
                variant="outline"
                size="lg"
                onClick={handlePrevious}
                className="flex-1"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Previous
              </Button>
            )}
            
            {currentStep < steps.length - 1 ? (
              <Button
                type="button"
                variant="primary"
                size="lg"
                onClick={handleNext}
                disabled={!validateStep()}
                className="flex-1"
              >
                Next
                <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Button>
            ) : (
              <Button
                type="submit"
                variant="primary"
                size="lg"
                disabled={!validateStep()}
                className="flex-1"
              >
                Generate My Roadmap
                <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </Button>
            )}
          </div>

          {/* Step Indicators */}
          <div className="flex justify-center gap-2 pt-4">
            {steps.map((_, index) => (
              <button
                key={index}
                type="button"
                onClick={() => setCurrentStep(index)}
                className={`w-2.5 h-2.5 rounded-full transition-all duration-200 ${
                  index === currentStep 
                    ? 'bg-[var(--color-accent)] w-8' 
                    : index < currentStep
                    ? 'bg-[var(--color-accent)] opacity-50'
                    : 'bg-gray-300'
                }`}
                aria-label={`Go to step ${index + 1}`}
              />
            ))}
          </div>
        </form>
      </Card>
    </div>
  );
}

export default RoadmapForm;
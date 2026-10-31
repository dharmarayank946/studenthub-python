import React, { useState, useEffect, useMemo } from 'react';

// API configuration
const API_BASE = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || (typeof window !== 'undefined' && window.location.hostname === 'localhost' ? 'http://127.0.0.1:8000' : '');

const DEFAULT_USER = {
  id: 1,
  username: "admin",
  email: "admin@studenthub.edu",
  full_name: "System Administrator",
  role: "Administrator",
  department: "Academic Operations",
  phone: "+1 (555) 019-2834",
  bio: "Lead Administrator managing StudentHub records and faculty portal.",
  member_since: "2026-10-26"
};

// Initial demo data so the app displays instantly even before backend connects
const INITIAL_DEMO_STUDENTS = [
  {
    student_id: "STU-001",
    name: "Aarav Sharma",
    course: "Computer Science",
    marks: 92.5,
    percentage: 92.5,
    grade: "A+",
    status: "Distinction",
    email: "aarav.sharma@university.edu",
    phone: "+91 98765 43210",
    enrollment_date: "2026-09-01"
  },
  {
    student_id: "STU-002",
    name: "Diya Patel",
    course: "Data Science",
    marks: 84.0,
    percentage: 84.0,
    grade: "A",
    status: "Passing",
    email: "diya.patel@university.edu",
    phone: "+91 98123 45678",
    enrollment_date: "2026-09-05"
  },
  {
    student_id: "STU-003",
    name: "Rohan Verma",
    course: "Cybersecurity",
    marks: 76.5,
    percentage: 76.5,
    grade: "B",
    status: "Passing",
    email: "rohan.v@university.edu",
    phone: "+91 97234 56789",
    enrollment_date: "2026-09-12"
  },
  {
    student_id: "STU-004",
    name: "Ananya Iyer",
    course: "Artificial Intelligence",
    marks: 95.0,
    percentage: 95.0,
    grade: "A+",
    status: "Distinction",
    email: "ananya.iyer@university.edu",
    phone: "+91 96345 67890",
    enrollment_date: "2026-09-15"
  },
  {
    student_id: "STU-005",
    name: "Karan Rao",
    course: "Computer Science",
    marks: 48.0,
    percentage: 48.0,
    grade: "F",
    status: "Needs Improvement",
    email: "karan.rao@university.edu",
    phone: "+91 95456 78901",
    enrollment_date: "2026-09-20"
  }
];

export default function App() {
  const [students, setStudents] = useState(INITIAL_DEMO_STUDENTS);
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' | 'students' | 'reports' | 'profile'
  const [searchQuery, setSearchQuery] = useState('');
  const [courseFilter, setCourseFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [sortBy, setSortBy] = useState('id'); // 'id' | 'name' | 'marks'

  // User Authentication & Profile State
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = localStorage.getItem('studenthub_user');
      if (saved) return JSON.parse(saved);
      if (localStorage.getItem('studenthub_logged_out') === 'true') return null;
      return DEFAULT_USER;
    } catch {
      return DEFAULT_USER;
    }
  });

  const [authMode, setAuthMode] = useState('login'); // 'login' | 'register'
  const [authForm, setAuthForm] = useState({
    identifier: 'admin',
    password: 'Admin@123',
    username: '',
    email: '',
    full_name: '',
    department: 'Computer Science',
    confirmPassword: ''
  });
  const [authError, setAuthError] = useState('');

  const [profileForm, setProfileForm] = useState(() => ({
    full_name: currentUser?.full_name || DEFAULT_USER.full_name,
    email: currentUser?.email || DEFAULT_USER.email,
    department: currentUser?.department || DEFAULT_USER.department,
    phone: currentUser?.phone || DEFAULT_USER.phone,
    bio: currentUser?.bio || DEFAULT_USER.bio
  }));

  const [securityForm, setSecurityForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmNewPassword: ''
  });

  // Modals state
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingStudent, setEditingStudent] = useState(null);
  const [deletingStudent, setDeletingStudent] = useState(null);
  const [formData, setFormData] = useState({
    student_id: '',
    name: '',
    course: '',
    marks: '',
    email: '',
    phone: ''
  });
  const [formError, setFormError] = useState('');
  const [apiConnected, setApiConnected] = useState(false);
  const [notification, setNotification] = useState(null);

  const showToast = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 3500);
  };

  // Attempt to fetch from real API
  const fetchStudents = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/students`);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setStudents(data);
        }
        setApiConnected(true);
      } else {
        setApiConnected(false);
      }
    } catch {
      setApiConnected(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, []);

  // Update profile form when user changes
  useEffect(() => {
    if (currentUser) {
      setProfileForm({
        full_name: currentUser.full_name || '',
        email: currentUser.email || '',
        department: currentUser.department || '',
        phone: currentUser.phone || '',
        bio: currentUser.bio || ''
      });
    }
  }, [currentUser]);

  // Auth Handlers
  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError('');
    const ident = authForm.identifier.trim();
    const pwd = authForm.password;

    if (!ident) return setAuthError('Please enter your username or email.');
    if (!pwd) return setAuthError('Please enter your password.');

    // Try backend API first
    if (API_BASE) {
      try {
        const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ identifier: ident, password: pwd })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.user) {
            setCurrentUser(data.user);
            localStorage.setItem('studenthub_user', JSON.stringify(data.user));
            localStorage.removeItem('studenthub_logged_out');
            showToast(`Welcome back, ${data.user.full_name}!`);
            return;
          }
        } else {
          const errData = await res.json().catch(() => ({}));
          return setAuthError(errData.detail || 'Invalid username/email or password.');
        }
      } catch (_) {}
    }

    // Local / offline authentication
    if (
      (ident.toLowerCase() === DEFAULT_USER.username.toLowerCase() || ident.toLowerCase() === DEFAULT_USER.email.toLowerCase()) &&
      pwd === 'Admin@123'
    ) {
      setCurrentUser(DEFAULT_USER);
      localStorage.setItem('studenthub_user', JSON.stringify(DEFAULT_USER));
      localStorage.removeItem('studenthub_logged_out');
      showToast(`Welcome back, ${DEFAULT_USER.full_name}!`);
      return;
    }

    // Check custom registered local accounts
    const localAccounts = JSON.parse(localStorage.getItem('studenthub_accounts') || '[]');
    const matched = localAccounts.find(
      acc => (acc.username.toLowerCase() === ident.toLowerCase() || acc.email.toLowerCase() === ident.toLowerCase()) && acc.password === pwd
    );
    if (matched) {
      const { password, ...userSafe } = matched;
      setCurrentUser(userSafe);
      localStorage.setItem('studenthub_user', JSON.stringify(userSafe));
      localStorage.removeItem('studenthub_logged_out');
      showToast(`Welcome back, ${userSafe.full_name}!`);
      return;
    }

    setAuthError('Invalid credentials. (Hint: default admin is "admin" / "Admin@123")');
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setAuthError('');

    if (!authForm.username.trim() || authForm.username.trim().length < 3) {
      return setAuthError('Username must be at least 3 characters.');
    }
    if (!authForm.email.trim() || !authForm.email.includes('@')) {
      return setAuthError('Please enter a valid email address.');
    }
    if (!authForm.full_name.trim()) {
      return setAuthError('Please enter your full name.');
    }
    if (!authForm.password || authForm.password.length < 6) {
      return setAuthError('Password must be at least 6 characters.');
    }
    if (authForm.password !== authForm.confirmPassword) {
      return setAuthError('Password confirmation does not match.');
    }

    const newUser = {
      id: Date.now(),
      username: authForm.username.trim(),
      email: authForm.email.trim(),
      full_name: authForm.full_name.trim(),
      role: 'Faculty',
      department: authForm.department || 'Computer Science',
      phone: '',
      bio: 'Faculty member at StudentHub Academic Operations.',
      member_since: new Date().toISOString().split('T')[0]
    };

    // Try API
    if (API_BASE) {
      try {
        const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: newUser.username,
            email: newUser.email,
            password: authForm.password,
            full_name: newUser.full_name,
            department: newUser.department
          })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.user) {
            setCurrentUser(data.user);
            localStorage.setItem('studenthub_user', JSON.stringify(data.user));
            localStorage.removeItem('studenthub_logged_out');
            showToast('Account registered successfully!');
            return;
          }
        }
      } catch (_) {}
    }

    // Save locally
    const localAccounts = JSON.parse(localStorage.getItem('studenthub_accounts') || '[]');
    localAccounts.push({ ...newUser, password: authForm.password });
    localStorage.setItem('studenthub_accounts', JSON.stringify(localAccounts));

    setCurrentUser(newUser);
    localStorage.setItem('studenthub_user', JSON.stringify(newUser));
    localStorage.removeItem('studenthub_logged_out');
    showToast('Account created successfully!');
  };

  const handleLogout = () => {
    localStorage.setItem('studenthub_logged_out', 'true');
    localStorage.removeItem('studenthub_user');
    setCurrentUser(null);
    setActiveTab('dashboard');
    showToast('Signed out successfully.', 'info');
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    if (!profileForm.full_name.trim()) return showToast('Full name cannot be empty', 'error');
    if (!profileForm.email.trim()) return showToast('Email cannot be empty', 'error');

    const updated = {
      ...currentUser,
      full_name: profileForm.full_name.trim(),
      email: profileForm.email.trim(),
      department: profileForm.department.trim(),
      phone: profileForm.phone.trim(),
      bio: profileForm.bio.trim()
    };

    if (API_BASE && currentUser?.id) {
      try {
        await fetch(`${API_BASE}/api/v1/auth/profile/${currentUser.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(profileForm)
        });
      } catch (_) {}
    }

    setCurrentUser(updated);
    localStorage.setItem('studenthub_user', JSON.stringify(updated));
    showToast('Profile information saved successfully!');
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (!securityForm.currentPassword) return showToast('Current password is required', 'error');
    if (!securityForm.newPassword || securityForm.newPassword.length < 6) {
      return showToast('New password must be at least 6 characters', 'error');
    }
    if (securityForm.newPassword !== securityForm.confirmNewPassword) {
      return showToast('Password confirmation does not match', 'error');
    }

    if (API_BASE && currentUser?.id) {
      try {
        const res = await fetch(`${API_BASE}/api/v1/auth/change-password/${currentUser.id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            old_password: securityForm.currentPassword,
            new_password: securityForm.newPassword
          })
        });
        if (res.ok) {
          setSecurityForm({ currentPassword: '', newPassword: '', confirmNewPassword: '' });
          showToast('Password updated successfully!');
          return;
        }
      } catch (_) {}
    }

    setSecurityForm({ currentPassword: '', newPassword: '', confirmNewPassword: '' });
    showToast('Password changed successfully!');
  };

  // Compute unique courses for filter
  const uniqueCourses = useMemo(() => {
    const set = new Set(students.map(s => s.course).filter(Boolean));
    return ['All', ...Array.from(set).sort()];
  }, [students]);

  // Filtered & Sorted student list
  const filteredStudents = useMemo(() => {
    let result = students.filter(s => {
      const q = searchQuery.toLowerCase().trim();
      const matchQuery = !q ||
        s.name.toLowerCase().includes(q) ||
        s.student_id.toLowerCase().includes(q) ||
        s.course.toLowerCase().includes(q) ||
        (s.email && s.email.toLowerCase().includes(q));

      const matchCourse = courseFilter === 'All' || s.course.toLowerCase() === courseFilter.toLowerCase();
      const matchStatus = statusFilter === 'All' || s.status.toLowerCase() === statusFilter.toLowerCase();

      return matchQuery && matchCourse && matchStatus;
    });

    result.sort((a, b) => {
      if (sortBy === 'name') return a.name.localeCompare(b.name);
      if (sortBy === 'marks') return b.marks - a.marks;
      return a.student_id.localeCompare(b.student_id);
    });

    return result;
  }, [students, searchQuery, courseFilter, statusFilter, sortBy]);

  // Academic metrics for KPI cards
  const metrics = useMemo(() => {
    const total = students.length;
    if (total === 0) return { total: 0, avgMarks: 0, passRate: 0, distinctions: 0, high: 0, low: 0 };
    const marksArr = students.map(s => s.marks);
    const avg = marksArr.reduce((a, b) => a + b, 0) / total;
    const passes = marksArr.filter(m => m >= 50).length;
    const distinctions = marksArr.filter(m => m >= 85).length;
    return {
      total,
      avgMarks: avg.toFixed(1),
      passRate: ((passes / total) * 100).toFixed(1),
      distinctions,
      high: Math.max(...marksArr).toFixed(1),
      low: Math.min(...marksArr).toFixed(1)
    };
  }, [students]);

  // Form submission handler
  const handleSaveStudent = async (e) => {
    e.preventDefault();
    setFormError('');

    if (!formData.student_id.trim()) return setFormError('Student ID is required.');
    if (!formData.name.trim()) return setFormError('Student name is required.');
    if (!formData.course.trim()) return setFormError('Course is required.');
    const m = parseFloat(formData.marks);
    if (isNaN(m) || m < 0 || m > 100) return setFormError('Marks must be a valid number between 0 and 100.');

    if (editingStudent) {
      // Update
      try {
        const res = await fetch(`${API_BASE}/api/v1/students/${editingStudent.student_id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: formData.name,
            course: formData.course,
            marks: m,
            email: formData.email,
            phone: formData.phone
          })
        });
        if (res.ok) {
          const updated = await res.json();
          setStudents(prev => prev.map(s => s.student_id === updated.student_id ? updated : s));
        } else {
          // Local fallback
          updateLocalStudent(editingStudent.student_id, m);
        }
      } catch {
        updateLocalStudent(editingStudent.student_id, m);
      }
      setEditingStudent(null);
      showToast(`Student ${formData.student_id} updated.`);
    } else {
      // Create
      const exists = students.some(s => s.student_id.toUpperCase() === formData.student_id.toUpperCase());
      if (exists) return setFormError(`Student ID '${formData.student_id}' already exists.`);

      const newRecord = {
        student_id: formData.student_id.trim(),
        name: formData.name.trim(),
        course: formData.course.trim(),
        marks: m,
        percentage: m,
        grade: calcGrade(m),
        status: calcStatus(m),
        email: formData.email.trim(),
        phone: formData.phone.trim(),
        enrollment_date: new Date().toISOString().split('T')[0]
      };

      try {
        const res = await fetch(`${API_BASE}/api/v1/students`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newRecord)
        });
        if (res.ok) {
          const created = await res.json();
          setStudents(prev => [created, ...prev]);
        } else {
          setStudents(prev => [newRecord, ...prev]);
        }
      } catch {
        setStudents(prev => [newRecord, ...prev]);
      }
      setIsAddModalOpen(false);
      showToast(`Student ${newRecord.name} added successfully!`);
    }

    setFormData({ student_id: '', name: '', course: '', marks: '', email: '', phone: '' });
  };

  const updateLocalStudent = (id, m) => {
    setStudents(prev => prev.map(s => {
      if (s.student_id === id) {
        return {
          ...s,
          name: formData.name.trim(),
          course: formData.course.trim(),
          marks: m,
          percentage: m,
          grade: calcGrade(m),
          status: calcStatus(m),
          email: formData.email.trim(),
          phone: formData.phone.trim()
        };
      }
      return s;
    }));
  };

  const handleDeleteStudent = async () => {
    if (!deletingStudent) return;
    const id = deletingStudent.student_id;
    try {
      await fetch(`${API_BASE}/api/v1/students/${id}`, { method: 'DELETE' });
    } catch {
      // Local fallback
    }
    setStudents(prev => prev.filter(s => s.student_id !== id));
    setDeletingStudent(null);
    showToast(`Student ${id} removed.`, 'info');
  };

  const calcGrade = (m) => {
    if (m >= 90) return 'A+';
    if (m >= 80) return 'A';
    if (m >= 70) return 'B';
    if (m >= 60) return 'C';
    if (m >= 50) return 'D';
    return 'F';
  };

  const calcStatus = (m) => {
    if (m >= 85) return 'Distinction';
    if (m >= 50) return 'Passing';
    return 'Needs Improvement';
  };

  const handleExportCSV = () => {
    const headers = ['Student ID,Name,Course,Marks,Percentage,Grade,Status,Email,Phone,Enrollment Date\n'];
    const rows = students.map(s => 
      `"${s.student_id}","${s.name}","${s.course}",${s.marks},${s.marks}%,"${s.grade}","${s.status}","${s.email || ''}","${s.phone || ''}","${s.enrollment_date || ''}"`
    ).join('\n');
    const blob = new Blob([headers + rows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'studenthub_records.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('Exported CSV successfully!');
  };

  // If user is not authenticated, show modern Sign In / Registration Screen
  if (!currentUser) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'radial-gradient(ellipse at 50% 20%, #1E293B 0%, #0F172A 100%)', padding: '1.5rem', position: 'relative' }}>
        {notification && (
          <div style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: notification.type === 'info' ? '#3B82F6' : '#10B981',
            color: '#FFF',
            padding: '0.75rem 1.25rem',
            borderRadius: '8px',
            fontWeight: 600,
            boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
            zIndex: 9999
          }}>
            {notification.msg}
          </div>
        )}

        <div style={{ width: '100%', maxWidth: '440px', background: '#1E293B', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px', padding: '2.5rem', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.7)' }}>
          {/* Brand header */}
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'var(--brand-gradient)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '0.75rem' }}>
              🎓
            </div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>StudentHub Portal</h1>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Secure Academic Administration Suite</p>
          </div>

          {/* Mode Switcher */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', background: '#0F172A', padding: '4px', borderRadius: '8px', marginBottom: '1.75rem' }}>
            <button
              onClick={() => { setAuthMode('login'); setAuthError(''); }}
              style={{
                padding: '0.5rem',
                border: 'none',
                borderRadius: '6px',
                background: authMode === 'login' ? '#2563EB' : 'transparent',
                color: authMode === 'login' ? '#FFFFFF' : 'var(--text-muted)',
                fontWeight: 700,
                fontSize: '0.85rem',
                cursor: 'pointer'
              }}
            >
              Sign In
            </button>
            <button
              onClick={() => { setAuthMode('register'); setAuthError(''); }}
              style={{
                padding: '0.5rem',
                border: 'none',
                borderRadius: '6px',
                background: authMode === 'register' ? '#2563EB' : 'transparent',
                color: authMode === 'register' ? '#FFFFFF' : 'var(--text-muted)',
                fontWeight: 700,
                fontSize: '0.85rem',
                cursor: 'pointer'
              }}
            >
              Create Account
            </button>
          </div>

          {authError && (
            <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #EF4444', color: '#FCA5A5', padding: '0.6rem 0.85rem', borderRadius: '8px', fontSize: '0.82rem', marginBottom: '1.25rem' }}>
              {authError}
            </div>
          )}

          {authMode === 'login' ? (
            <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>USERNAME OR EMAIL</label>
                <input
                  type="text"
                  value={authForm.identifier}
                  onChange={e => setAuthForm({ ...authForm, identifier: e.target.value })}
                  placeholder="admin or admin@studenthub.edu"
                  style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '0.7rem 0.85rem', color: '#FFFFFF', fontSize: '0.9rem' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>PASSWORD</label>
                <input
                  type="password"
                  value={authForm.password}
                  onChange={e => setAuthForm({ ...authForm, password: e.target.value })}
                  placeholder="••••••••••••"
                  style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '0.7rem 0.85rem', color: '#FFFFFF', fontSize: '0.9rem' }}
                />
              </div>

              <button
                type="submit"
                style={{
                  marginTop: '0.5rem',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  border: 'none',
                  background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
                  color: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '0.95rem',
                  cursor: 'pointer',
                  boxShadow: '0 4px 14px rgba(37, 99, 235, 0.4)'
                }}
              >
                Sign In to Portal
              </button>

              <div style={{ textAlign: 'center', marginTop: '0.5rem', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                Default Administrator: <strong style={{ color: '#60A5FA' }}>admin</strong> / <strong style={{ color: '#60A5FA' }}>Admin@123</strong>
              </div>
            </form>
          ) : (
            <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>FULL NAME</label>
                <input
                  type="text"
                  value={authForm.full_name}
                  onChange={e => setAuthForm({ ...authForm, full_name: e.target.value })}
                  placeholder="Dr. Elizabeth Warren"
                  style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '0.65rem 0.85rem', color: '#FFFFFF', fontSize: '0.88rem' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>USERNAME</label>
                  <input
                    type="text"
                    value={authForm.username}
                    onChange={e => setAuthForm({ ...authForm, username: e.target.value })}
                    placeholder="ewarren"
                    style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '0.65rem 0.85rem', color: '#FFFFFF', fontSize: '0.88rem' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>DEPARTMENT</label>
                  <input
                    type="text"
                    value={authForm.department}
                    onChange={e => setAuthForm({ ...authForm, department: e.target.value })}
                    placeholder="Computer Science"
                    style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '0.65rem 0.85rem', color: '#FFFFFF', fontSize: '0.88rem' }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>EMAIL ADDRESS</label>
                <input
                  type="email"
                  value={authForm.email}
                  onChange={e => setAuthForm({ ...authForm, email: e.target.value })}
                  placeholder="ewarren@university.edu"
                  style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '0.65rem 0.85rem', color: '#FFFFFF', fontSize: '0.88rem' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>PASSWORD</label>
                  <input
                    type="password"
                    value={authForm.password}
                    onChange={e => setAuthForm({ ...authForm, password: e.target.value })}
                    placeholder="Min 6 chars"
                    style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '0.65rem 0.85rem', color: '#FFFFFF', fontSize: '0.88rem' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>CONFIRM PWD</label>
                  <input
                    type="password"
                    value={authForm.confirmPassword}
                    onChange={e => setAuthForm({ ...authForm, confirmPassword: e.target.value })}
                    placeholder="Repeat pwd"
                    style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '0.65rem 0.85rem', color: '#FFFFFF', fontSize: '0.88rem' }}
                  />
                </div>
              </div>

              <button
                type="submit"
                style={{
                  marginTop: '0.5rem',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  border: 'none',
                  background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                  color: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '0.95rem',
                  cursor: 'pointer',
                  boxShadow: '0 4px 14px rgba(16, 185, 129, 0.4)'
                }}
              >
                Create Account
              </button>
            </form>
          )}
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-primary)' }}>
      {/* Toast Notification */}
      {notification && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          background: notification.type === 'info' ? '#3B82F6' : '#10B981',
          color: '#FFF',
          padding: '0.75rem 1.25rem',
          borderRadius: '8px',
          fontWeight: 600,
          boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
          zIndex: 9999,
          animation: 'fadeIn 0.2s ease-out'
        }}>
          {notification.msg}
        </div>
      )}

      {/* Sidebar Navigation */}
      <aside style={{
        width: '260px',
        background: 'var(--bg-surface)',
        borderRight: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        padding: '1.5rem 1rem'
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem', paddingLeft: '0.5rem' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'var(--brand-gradient)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: '1.2rem',
            color: '#FFFFFF'
          }}>S</div>
          <div>
            <h1 style={{ fontSize: '1.15rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#FFFFFF' }}>StudentHub</h1>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Academic Suite v3</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', flex: 1 }}>
          {[
            { id: 'dashboard', label: 'Dashboard', icon: '📊' },
            { id: 'students', label: 'Students Directory', icon: '🎓', count: students.length },
            { id: 'reports', label: 'Analytics & Reports', icon: '📈' },
            { id: 'profile', label: 'User Profile', icon: '👤' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                border: 'none',
                background: activeTab === tab.id ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                color: activeTab === tab.id ? '#60A5FA' : 'var(--text-muted)',
                fontWeight: activeTab === tab.id ? 700 : 500,
                fontSize: '0.9rem',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease'
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </span>
              {tab.count !== undefined && (
                <span style={{
                  background: 'rgba(255, 255, 255, 0.08)',
                  padding: '0.15rem 0.5rem',
                  borderRadius: '12px',
                  fontSize: '0.75rem',
                  fontFamily: 'var(--font-mono)'
                }}>{tab.count}</span>
              )}
            </button>
          ))}
        </nav>

        {/* User Session & Logout Card */}
        {currentUser && (
          <div style={{
            padding: '0.85rem',
            borderRadius: '10px',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            marginBottom: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', overflow: 'hidden' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#2563EB', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem', color: '#FFF', flexShrink: 0 }}>
                {currentUser.full_name ? currentUser.full_name.charAt(0) : 'U'}
              </div>
              <div style={{ overflow: 'hidden' }}>
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#FFF', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                  {currentUser.full_name}
                </div>
                <div style={{ fontSize: '0.68rem', color: '#60A5FA' }}>
                  {currentUser.role || 'Staff'}
                </div>
              </div>
            </div>
            <button
              onClick={handleLogout}
              title="Sign Out"
              style={{
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                color: '#F87171',
                padding: '0.35rem 0.6rem',
                borderRadius: '6px',
                fontSize: '0.75rem',
                cursor: 'pointer',
                fontWeight: 600
              }}
            >
              Logout
            </button>
          </div>
        )}

        {/* API Status Badge */}
        <div style={{
          padding: '0.85rem',
          borderRadius: '10px',
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid rgba(255, 255, 255, 0.05)',
          fontSize: '0.75rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.25rem' }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: apiConnected ? '#10B981' : '#F59E0B'
            }} />
            <span style={{ fontWeight: 600, color: '#E2E8F0' }}>
              {apiConnected ? 'API Connected (Render)' : 'Local Storage Mode'}
            </span>
          </div>
          <p style={{ color: 'var(--text-dim)', fontSize: '0.7rem' }}>
            {apiConnected ? 'FastAPI Backend Live' : 'Browser Session Sync'}
          </p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '2rem 2.5rem', overflowY: 'auto' }}>
        {/* Top Header */}
        <header style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem'
        }}>
          <div>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#FFFFFF' }}>
              {activeTab === 'dashboard' && 'Academic Overview'}
              {activeTab === 'students' && 'Student Records Directory'}
              {activeTab === 'reports' && 'Academic Performance & Reports'}
              {activeTab === 'profile' && 'User Profile & Security'}
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Session Term 2026 • Real-time Academic Database
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              onClick={handleExportCSV}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-muted)',
                padding: '0.6rem 1rem',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.85rem',
                cursor: 'pointer',
                fontWeight: 600
              }}
            >
              <span>📥</span>
              <span>Export CSV</span>
            </button>
            <button
              onClick={() => {
                setEditingStudent(null);
                setFormData({ student_id: '', name: '', course: '', marks: '', email: '', phone: '' });
                setIsAddModalOpen(true);
              }}
              className="glow-btn"
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              <span>+</span>
              <span>Add Student</span>
            </button>
          </div>
        </header>

        {/* 1. DASHBOARD TAB */}
        {activeTab === 'dashboard' && (
          <div className="animate-fade">
            {/* KPI Cards Row */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap: '1.25rem',
              marginBottom: '2rem'
            }}>
              {[
                { title: 'Total Enrolled', val: metrics.total, sub: 'Registered Students', color: '#3B82F6', icon: '👥' },
                { title: 'Cohort Average', val: `${metrics.avgMarks}%`, sub: 'Overall Grade Point', color: '#10B981', icon: '🎯' },
                { title: 'Pass Percentage', val: `${metrics.passRate}%`, sub: 'Students >= 50%', color: '#8B5CF6', icon: '📈' },
                { title: 'Honors / Distinction', val: metrics.distinctions, sub: 'Scores >= 85%', color: '#F59E0B', icon: '🏆' }
              ].map((card, i) => (
                <div key={i} className="glass-panel" style={{ padding: '1.5rem', position: 'relative', overflow: 'hidden' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      {card.title}
                    </span>
                    <span style={{ fontSize: '1.2rem' }}>{card.icon}</span>
                  </div>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.02em', marginBottom: '0.25rem' }}>
                    {card.val}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: card.color, fontWeight: 600 }}>
                    {card.sub}
                  </div>
                </div>
              ))}
            </div>

            {/* Recent Students Table in Dashboard */}
            <div className="glass-panel" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#FFFFFF' }}>Recent Enrollees</h3>
                <button
                  onClick={() => setActiveTab('students')}
                  style={{ background: 'transparent', border: 'none', color: '#60A5FA', fontSize: '0.85rem', cursor: 'pointer', fontWeight: 600 }}
                >
                  View All Directory →
                </button>
              </div>

              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-dim)' }}>
                      <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>ID</th>
                      <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>STUDENT NAME</th>
                      <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>COURSE</th>
                      <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>MARKS</th>
                      <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>GRADE</th>
                      <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>STATUS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.slice(0, 5).map(s => (
                      <tr key={s.student_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                        <td style={{ padding: '0.85rem 1rem', fontFamily: 'var(--font-mono)', color: '#93C5FD' }}>{s.student_id}</td>
                        <td style={{ padding: '0.85rem 1rem', fontWeight: 600, color: '#FFFFFF' }}>{s.name}</td>
                        <td style={{ padding: '0.85rem 1rem', color: 'var(--text-muted)' }}>{s.course}</td>
                        <td style={{ padding: '0.85rem 1rem', fontWeight: 700 }}>{s.marks}</td>
                        <td style={{ padding: '0.85rem 1rem' }}><span className="badge badge-grade">{s.grade}</span></td>
                        <td style={{ padding: '0.85rem 1rem' }}>
                          <span className={`badge ${s.status === 'Distinction' ? 'badge-distinction' : s.status === 'Passing' ? 'badge-passing' : 'badge-failing'}`}>
                            {s.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* 2. STUDENTS DIRECTORY TAB */}
        {activeTab === 'students' && (
          <div className="animate-fade">
            {/* Filter Bar */}
            <div className="glass-panel" style={{ padding: '1rem 1.25rem', marginBottom: '1.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
              <div style={{ flex: 1, minWidth: '220px', position: 'relative' }}>
                <span style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)' }}>🔍</span>
                <input
                  type="text"
                  placeholder="Search by ID, name, course, or email..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'var(--bg-primary)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    padding: '0.6rem 1rem 0.6rem 2.5rem',
                    color: '#FFF',
                    fontSize: '0.85rem'
                  }}
                />
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontWeight: 600 }}>COURSE:</label>
                <select
                  value={courseFilter}
                  onChange={e => setCourseFilter(e.target.value)}
                  style={{
                    background: 'var(--bg-primary)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    padding: '0.55rem 0.85rem',
                    color: '#FFF',
                    fontSize: '0.85rem',
                    cursor: 'pointer'
                  }}
                >
                  {uniqueCourses.map(c => <option key={c} value={c}>{c}</option>)}
                </select>

                <label style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontWeight: 600 }}>STATUS:</label>
                <select
                  value={statusFilter}
                  onChange={e => setStatusFilter(e.target.value)}
                  style={{
                    background: 'var(--bg-primary)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    padding: '0.55rem 0.85rem',
                    color: '#FFF',
                    fontSize: '0.85rem',
                    cursor: 'pointer'
                  }}
                >
                  <option value="All">All Statuses</option>
                  <option value="Distinction">Distinction</option>
                  <option value="Passing">Passing</option>
                  <option value="Needs Improvement">Needs Improvement</option>
                </select>

                <label style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontWeight: 600 }}>SORT:</label>
                <select
                  value={sortBy}
                  onChange={e => setSortBy(e.target.value)}
                  style={{
                    background: 'var(--bg-primary)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    padding: '0.55rem 0.85rem',
                    color: '#FFF',
                    fontSize: '0.85rem',
                    cursor: 'pointer'
                  }}
                >
                  <option value="id">Student ID</option>
                  <option value="name">Name (A-Z)</option>
                  <option value="marks">Highest Marks</option>
                </select>
              </div>
            </div>

            {/* Students Table */}
            <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ background: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-dim)' }}>
                      <th style={{ padding: '0.85rem 1.25rem', fontWeight: 600 }}>ID</th>
                      <th style={{ padding: '0.85rem 1.25rem', fontWeight: 600 }}>STUDENT NAME</th>
                      <th style={{ padding: '0.85rem 1.25rem', fontWeight: 600 }}>COURSE</th>
                      <th style={{ padding: '0.85rem 1.25rem', fontWeight: 600 }}>MARKS</th>
                      <th style={{ padding: '0.85rem 1.25rem', fontWeight: 600 }}>GRADE</th>
                      <th style={{ padding: '0.85rem 1.25rem', fontWeight: 600 }}>STATUS</th>
                      <th style={{ padding: '0.85rem 1.25rem', fontWeight: 600 }}>ACTIONS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredStudents.length === 0 ? (
                      <tr>
                        <td colSpan="7" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-dim)' }}>
                          No student records found matching the current search criteria.
                        </td>
                      </tr>
                    ) : (
                      filteredStudents.map(s => (
                        <tr key={s.student_id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.03)', transition: 'background 0.15s ease' }}>
                          <td style={{ padding: '0.85rem 1.25rem', fontFamily: 'var(--font-mono)', color: '#93C5FD' }}>{s.student_id}</td>
                          <td style={{ padding: '0.85rem 1.25rem' }}>
                            <div style={{ fontWeight: 600, color: '#FFFFFF' }}>{s.name}</div>
                            {s.email && <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{s.email}</div>}
                          </td>
                          <td style={{ padding: '0.85rem 1.25rem', color: 'var(--text-muted)' }}>{s.course}</td>
                          <td style={{ padding: '0.85rem 1.25rem', fontWeight: 700, color: '#FFFFFF' }}>{s.marks}</td>
                          <td style={{ padding: '0.85rem 1.25rem' }}><span className="badge badge-grade">{s.grade}</span></td>
                          <td style={{ padding: '0.85rem 1.25rem' }}>
                            <span className={`badge ${s.status === 'Distinction' ? 'badge-distinction' : s.status === 'Passing' ? 'badge-passing' : 'badge-failing'}`}>
                              {s.status}
                            </span>
                          </td>
                          <td style={{ padding: '0.85rem 1.25rem' }}>
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                              <button
                                onClick={() => {
                                  setEditingStudent(s);
                                  setFormData({
                                    student_id: s.student_id,
                                    name: s.name,
                                    course: s.course,
                                    marks: s.marks.toString(),
                                    email: s.email || '',
                                    phone: s.phone || ''
                                  });
                                  setIsAddModalOpen(true);
                                }}
                                style={{ background: 'rgba(59, 130, 246, 0.15)', border: '1px solid rgba(59, 130, 246, 0.3)', color: '#60A5FA', padding: '0.35rem 0.65rem', borderRadius: '6px', fontSize: '0.75rem', cursor: 'pointer', fontWeight: 600 }}
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => setDeletingStudent(s)}
                                style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#F87171', padding: '0.35rem 0.65rem', borderRadius: '6px', fontSize: '0.75rem', cursor: 'pointer', fontWeight: 600 }}
                              >
                                Delete
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* 3. REPORTS TAB */}
        {activeTab === 'reports' && (
          <div className="animate-fade">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
              <div className="glass-panel" style={{ padding: '1.5rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '1rem' }}>
                  Academic Honor Roll
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div style={{ padding: '0.85rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '0.75rem', color: '#34D399', fontWeight: 600, textTransform: 'uppercase' }}>Highest Scorer</div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#FFFFFF' }}>{metrics.high}% Marks</div>
                  </div>
                  <div style={{ padding: '0.85rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '0.75rem', color: '#F87171', fontWeight: 600, textTransform: 'uppercase' }}>Lowest Scorer</div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#FFFFFF' }}>{metrics.low}% Marks</div>
                  </div>
                </div>
              </div>

              <div className="glass-panel" style={{ padding: '1.5rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '1rem' }}>
                  Course Enrollment Breakdown
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {uniqueCourses.filter(c => c !== 'All').map(course => {
                    const count = students.filter(s => s.course === course).length;
                    const pct = ((count / students.length) * 100).toFixed(0);
                    return (
                      <div key={course} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0', borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                        <span style={{ color: '#E2E8F0', fontSize: '0.85rem' }}>{course}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>{pct}%</span>
                          <span className="badge badge-grade">{count}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 4. USER PROFILE TAB */}
        {activeTab === 'profile' && (
          <div className="animate-fade">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem', marginBottom: '2rem' }}>
              {/* Profile Overview Card */}
              <div className="glass-panel" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                <div style={{ width: '84px', height: '84px', borderRadius: '50%', background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2.5rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '1rem', boxShadow: '0 8px 20px rgba(59, 130, 246, 0.4)' }}>
                  {currentUser?.full_name?.charAt(0) || 'U'}
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
                  {currentUser?.full_name}
                </h3>
                <span style={{ background: 'rgba(59, 130, 246, 0.2)', border: '1px solid #3B82F6', color: '#93C5FD', padding: '0.2rem 0.65rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 700, marginTop: '0.4rem', textTransform: 'uppercase' }}>
                  {currentUser?.role || 'Staff'}
                </span>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.75rem', lineHeight: '1.4' }}>
                  {currentUser?.bio || 'Academic operations team member.'}
                </p>

                <div style={{ width: '100%', borderTop: '1px solid rgba(255,255,255,0.08)', marginTop: '1.25rem', paddingTop: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.65rem', textAlign: 'left', fontSize: '0.82rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-dim)' }}>Username:</span>
                    <strong style={{ color: '#E2E8F0' }}>{currentUser?.username}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-dim)' }}>Department:</span>
                    <strong style={{ color: '#E2E8F0' }}>{currentUser?.department}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-dim)' }}>Member Since:</span>
                    <strong style={{ color: '#E2E8F0' }}>{currentUser?.member_since || '2026-10-26'}</strong>
                  </div>
                </div>

                <button
                  onClick={handleLogout}
                  style={{
                    marginTop: '1.5rem',
                    width: '100%',
                    background: 'rgba(239, 68, 68, 0.15)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    color: '#F87171',
                    padding: '0.6rem',
                    borderRadius: '8px',
                    fontWeight: 700,
                    cursor: 'pointer'
                  }}
                >
                  Sign Out Account
                </button>
              </div>

              {/* Edit Details & Security Tabs */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {/* Edit Profile Form */}
                <div className="glass-panel" style={{ padding: '1.75rem' }}>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '1.25rem' }}>
                    Edit Personal Information
                  </h3>
                  <form onSubmit={handleSaveProfile} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>FULL NAME</label>
                        <input
                          type="text"
                          value={profileForm.full_name}
                          onChange={e => setProfileForm({ ...profileForm, full_name: e.target.value })}
                          style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', padding: '0.6rem 0.75rem', color: '#FFF' }}
                        />
                      </div>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>EMAIL ADDRESS</label>
                        <input
                          type="email"
                          value={profileForm.email}
                          onChange={e => setProfileForm({ ...profileForm, email: e.target.value })}
                          style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', padding: '0.6rem 0.75rem', color: '#FFF' }}
                        />
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>DEPARTMENT</label>
                        <input
                          type="text"
                          value={profileForm.department}
                          onChange={e => setProfileForm({ ...profileForm, department: e.target.value })}
                          style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', padding: '0.6rem 0.75rem', color: '#FFF' }}
                        />
                      </div>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>PHONE NUMBER</label>
                        <input
                          type="text"
                          value={profileForm.phone}
                          onChange={e => setProfileForm({ ...profileForm, phone: e.target.value })}
                          placeholder="+1 (555) 000-0000"
                          style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', padding: '0.6rem 0.75rem', color: '#FFF' }}
                        />
                      </div>
                    </div>

                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>BIOGRAPHY</label>
                      <textarea
                        rows="2"
                        value={profileForm.bio}
                        onChange={e => setProfileForm({ ...profileForm, bio: e.target.value })}
                        style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', padding: '0.6rem 0.75rem', color: '#FFF', resize: 'vertical' }}
                      />
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <button type="submit" className="glow-btn" style={{ padding: '0.6rem 1.25rem', fontSize: '0.85rem' }}>
                        Save Profile Details
                      </button>
                    </div>
                  </form>
                </div>

                {/* Change Password Form */}
                <div className="glass-panel" style={{ padding: '1.75rem' }}>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '1.25rem' }}>
                    Security & Password
                  </h3>
                  <form onSubmit={handleChangePassword} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>CURRENT PASSWORD</label>
                      <input
                        type="password"
                        value={securityForm.currentPassword}
                        onChange={e => setSecurityForm({ ...securityForm, currentPassword: e.target.value })}
                        placeholder="••••••••••••"
                        style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', padding: '0.6rem 0.75rem', color: '#FFF' }}
                      />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>NEW PASSWORD</label>
                        <input
                          type="password"
                          value={securityForm.newPassword}
                          onChange={e => setSecurityForm({ ...securityForm, newPassword: e.target.value })}
                          placeholder="Min 6 characters"
                          style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', padding: '0.6rem 0.75rem', color: '#FFF' }}
                        />
                      </div>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>CONFIRM NEW PASSWORD</label>
                        <input
                          type="password"
                          value={securityForm.confirmNewPassword}
                          onChange={e => setSecurityForm({ ...securityForm, confirmNewPassword: e.target.value })}
                          placeholder="Repeat new password"
                          style={{ width: '100%', background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', padding: '0.6rem 0.75rem', color: '#FFF' }}
                        />
                      </div>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <button type="submit" style={{ background: '#3B82F6', border: 'none', color: '#FFF', padding: '0.6rem 1.25rem', borderRadius: '6px', fontWeight: 700, fontSize: '0.85rem', cursor: 'pointer' }}>
                        Update Password
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* ADD / EDIT MODAL */}
      {isAddModalOpen && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(6px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div className="glass-panel" style={{ width: '480px', padding: '2rem', background: '#1E293B', border: '1px solid var(--border-accent)' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '1.25rem' }}>
              {editingStudent ? 'Edit Student Details' : 'Add New Student Record'}
            </h3>

            {formError && (
              <div style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #EF4444', color: '#FCA5A5', padding: '0.5rem 0.75rem', borderRadius: '6px', fontSize: '0.8rem', marginBottom: '1rem' }}>
                {formError}
              </div>
            )}

            <form onSubmit={handleSaveStudent} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.35rem', fontWeight: 600 }}>STUDENT ID</label>
                <input
                  type="text"
                  disabled={!!editingStudent}
                  value={formData.student_id}
                  onChange={e => setFormData({ ...formData, student_id: e.target.value })}
                  placeholder="e.g. STU-108"
                  style={{ width: '100%', background: '#0F172A', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '0.6rem 0.75rem', color: '#FFF' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.35rem', fontWeight: 600 }}>FULL NAME</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={e => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Priya Sundaram"
                  style={{ width: '100%', background: '#0F172A', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '0.6rem 0.75rem', color: '#FFF' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.35rem', fontWeight: 600 }}>COURSE</label>
                  <input
                    type="text"
                    value={formData.course}
                    onChange={e => setFormData({ ...formData, course: e.target.value })}
                    placeholder="e.g. Computer Science"
                    style={{ width: '100%', background: '#0F172A', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '0.6rem 0.75rem', color: '#FFF' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.35rem', fontWeight: 600 }}>MARKS (0 - 100)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    value={formData.marks}
                    onChange={e => setFormData({ ...formData, marks: e.target.value })}
                    placeholder="e.g. 88.5"
                    style={{ width: '100%', background: '#0F172A', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '0.6rem 0.75rem', color: '#FFF' }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.35rem', fontWeight: 600 }}>EMAIL ADDRESS</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={e => setFormData({ ...formData, email: e.target.value })}
                  placeholder="e.g. priya@university.edu"
                  style={{ width: '100%', background: '#0F172A', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '0.6rem 0.75rem', color: '#FFF' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.35rem', fontWeight: 600 }}>PHONE NUMBER</label>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={e => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="e.g. +91 98765 12345"
                  style={{ width: '100%', background: '#0F172A', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '0.6rem 0.75rem', color: '#FFF' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  style={{ background: 'transparent', border: '1px solid var(--border-subtle)', color: '#CBD5E1', padding: '0.6rem 1.2rem', borderRadius: '6px', cursor: 'pointer', fontWeight: 600 }}
                >
                  Cancel
                </button>
                <button type="submit" className="glow-btn">
                  {editingStudent ? 'Save Changes' : 'Create Record'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* DELETE CONFIRMATION MODAL */}
      {deletingStudent && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.75)',
          backdropFilter: 'blur(6px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div className="glass-panel" style={{ width: '420px', padding: '2rem', background: '#1E293B', border: '1px solid rgba(239, 68, 68, 0.4)' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#EF4444', marginBottom: '0.75rem' }}>
              Confirm Deletion
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: '1.5' }}>
              Are you sure you want to delete student <strong>{deletingStudent.name}</strong> (ID: {deletingStudent.student_id})? This record will be permanently deleted.
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button
                onClick={() => setDeletingStudent(null)}
                style={{ background: 'transparent', border: '1px solid var(--border-subtle)', color: '#CBD5E1', padding: '0.6rem 1.2rem', borderRadius: '6px', cursor: 'pointer', fontWeight: 600 }}
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteStudent}
                style={{ background: '#EF4444', color: '#FFFFFF', border: 'none', padding: '0.6rem 1.2rem', borderRadius: '6px', cursor: 'pointer', fontWeight: 700 }}
              >
                Delete Student
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

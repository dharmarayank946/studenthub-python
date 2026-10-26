import React, { useState, useEffect, useMemo } from 'react';

// API configuration
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

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
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' | 'students' | 'reports'
  const [searchQuery, setSearchQuery] = useState('');
  const [courseFilter, setCourseFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [sortBy, setSortBy] = useState('id'); // 'id' | 'name' | 'marks'
  
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
            { id: 'reports', label: 'Analytics & Reports', icon: '📈' }
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
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Session Term 2026 • Real-time Academic Database
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              onClick={handleExportCSV}
              style={{
                background: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid var(--border-subtle)',
                color: '#E2E8F0',
                padding: '0.6rem 1.1rem',
                borderRadius: '8px',
                fontWeight: 600,
                fontSize: '0.85rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem'
              }}
            >
              📥 Export CSV
            </button>
            <button
              onClick={() => {
                setEditingStudent(null);
                setFormData({ student_id: '', name: '', course: '', marks: '', email: '', phone: '' });
                setIsAddModalOpen(true);
              }}
              className="glow-btn"
            >
              ➕ Add Student
            </button>
          </div>
        </header>

        {/* TAB 1: DASHBOARD */}
        {activeTab === 'dashboard' && (
          <div className="animate-fade">
            {/* KPI Cards Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap: '1.25rem',
              marginBottom: '2rem'
            }}>
              {[
                { title: 'Total Enrolled', value: metrics.total, sub: 'Active candidates', icon: '👥', color: '#3B82F6' },
                { title: 'Class Average', value: `${metrics.avgMarks}%`, sub: 'Cumulative score', icon: '📊', color: '#06B6D4' },
                { title: 'Passing Rate', value: `${metrics.passRate}%`, sub: 'Above 50% marks', icon: '✅', color: '#10B981' },
                { title: 'Distinctions', value: metrics.distinctions, sub: '85%+ honors', icon: '🏆', color: '#F59E0B' }
              ].map((kpi, idx) => (
                <div key={idx} className="glass-panel" style={{ padding: '1.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>{kpi.title}</span>
                    <span style={{ fontSize: '1.2rem' }}>{kpi.icon}</span>
                  </div>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '0.2rem' }}>{kpi.value}</div>
                  <div style={{ fontSize: '0.75rem', color: kpi.color, fontWeight: 500 }}>{kpi.sub}</div>
                </div>
              ))}
            </div>

            {/* Quick Recent Directory Preview */}
            <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#FFFFFF' }}>Recent Student Records</h3>
                <button
                  onClick={() => setActiveTab('students')}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#60A5FA',
                    cursor: 'pointer',
                    fontSize: '0.85rem',
                    fontWeight: 600
                  }}
                >
                  View Full Directory →
                </button>
              </div>

              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-subtle)', textAlign: 'left', color: 'var(--text-muted)' }}>
                      <th style={{ padding: '0.75rem' }}>ID</th>
                      <th style={{ padding: '0.75rem' }}>Student Name</th>
                      <th style={{ padding: '0.75rem' }}>Course</th>
                      <th style={{ padding: '0.75rem' }}>Marks</th>
                      <th style={{ padding: '0.75rem' }}>Grade</th>
                      <th style={{ padding: '0.75rem' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.slice(0, 5).map(s => (
                      <tr key={s.student_id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                        <td style={{ padding: '0.75rem', fontFamily: 'var(--font-mono)', color: '#93C5FD' }}>{s.student_id}</td>
                        <td style={{ padding: '0.75rem', fontWeight: 600, color: '#F8FAFC' }}>{s.name}</td>
                        <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>{s.course}</td>
                        <td style={{ padding: '0.75rem' }}>
                          <span style={{ fontWeight: 700, color: '#FFFFFF' }}>{s.marks}%</span>
                        </td>
                        <td style={{ padding: '0.75rem' }}>
                          <span className="badge badge-grade">{s.grade}</span>
                        </td>
                        <td style={{ padding: '0.75rem' }}>
                          <span className={`badge ${s.status === 'Distinction' ? 'badge-distinction' : s.status === 'Passing' ? 'badge-passing' : 'badge-danger'}`}>
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

        {/* TAB 2: STUDENTS DIRECTORY */}
        {activeTab === 'students' && (
          <div className="animate-fade">
            {/* Filters & Search Toolbar */}
            <div className="glass-panel" style={{ padding: '1rem', marginBottom: '1.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
              <div style={{ flex: 1, minWidth: '220px' }}>
                <input
                  type="text"
                  placeholder="🔍 Search student name, ID, course, email..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'rgba(15, 23, 42, 0.6)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    padding: '0.65rem 1rem',
                    color: '#FFFFFF',
                    fontSize: '0.85rem'
                  }}
                />
              </div>

              {/* Course Filter */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Course:</span>
                <select
                  value={courseFilter}
                  onChange={e => setCourseFilter(e.target.value)}
                  style={{
                    background: 'rgba(15, 23, 42, 0.6)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    padding: '0.6rem 0.75rem',
                    color: '#FFFFFF',
                    fontSize: '0.85rem'
                  }}
                >
                  {uniqueCourses.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              {/* Status Filter */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Status:</span>
                <select
                  value={statusFilter}
                  onChange={e => setStatusFilter(e.target.value)}
                  style={{
                    background: 'rgba(15, 23, 42, 0.6)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    padding: '0.6rem 0.75rem',
                    color: '#FFFFFF',
                    fontSize: '0.85rem'
                  }}
                >
                  <option value="All">All Statuses</option>
                  <option value="Distinction">Distinction</option>
                  <option value="Passing">Passing</option>
                  <option value="Needs Improvement">Needs Improvement</option>
                </select>
              </div>

              {/* Sort By */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Sort:</span>
                <select
                  value={sortBy}
                  onChange={e => setSortBy(e.target.value)}
                  style={{
                    background: 'rgba(15, 23, 42, 0.6)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    padding: '0.6rem 0.75rem',
                    color: '#FFFFFF',
                    fontSize: '0.85rem'
                  }}
                >
                  <option value="id">Student ID</option>
                  <option value="name">Name</option>
                  <option value="marks">Highest Marks</option>
                </select>
              </div>
            </div>

            {/* Students Table */}
            <div className="glass-panel" style={{ padding: '1rem', overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', textAlign: 'left', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '0.75rem' }}>ID</th>
                    <th style={{ padding: '0.75rem' }}>Student Profile</th>
                    <th style={{ padding: '0.75rem' }}>Course</th>
                    <th style={{ padding: '0.75rem', width: '180px' }}>Academic Marks</th>
                    <th style={{ padding: '0.75rem' }}>Grade</th>
                    <th style={{ padding: '0.75rem' }}>Standing</th>
                    <th style={{ padding: '0.75rem', textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredStudents.length === 0 ? (
                    <tr>
                      <td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-dim)' }}>
                        No matching student records found.
                      </td>
                    </tr>
                  ) : (
                    filteredStudents.map(s => (
                      <tr key={s.student_id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                        <td style={{ padding: '0.85rem 0.75rem', fontFamily: 'var(--font-mono)', color: '#93C5FD', fontWeight: 600 }}>
                          {s.student_id}
                        </td>
                        <td style={{ padding: '0.85rem 0.75rem' }}>
                          <div style={{ fontWeight: 600, color: '#F8FAFC' }}>{s.name}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{s.email || 'No email registered'}</div>
                        </td>
                        <td style={{ padding: '0.85rem 0.75rem', color: 'var(--text-muted)' }}>
                          {s.course}
                        </td>
                        <td style={{ padding: '0.85rem 0.75rem' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '0.25rem' }}>
                            <span style={{ fontWeight: 700, color: '#FFFFFF' }}>{s.marks}%</span>
                          </div>
                          <div style={{ width: '100%', height: '6px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                            <div style={{
                              width: `${Math.min(s.marks, 100)}%`,
                              height: '100%',
                              background: s.marks >= 85 ? '#10B981' : s.marks >= 50 ? '#3B82F6' : '#EF4444'
                            }} />
                          </div>
                        </td>
                        <td style={{ padding: '0.85rem 0.75rem' }}>
                          <span className="badge badge-grade">{s.grade}</span>
                        </td>
                        <td style={{ padding: '0.85rem 0.75rem' }}>
                          <span className={`badge ${s.status === 'Distinction' ? 'badge-distinction' : s.status === 'Passing' ? 'badge-passing' : 'badge-danger'}`}>
                            {s.status}
                          </span>
                        </td>
                        <td style={{ padding: '0.85rem 0.75rem', textAlign: 'right' }}>
                          <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
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
                              style={{
                                background: 'rgba(59, 130, 246, 0.15)',
                                border: '1px solid rgba(59, 130, 246, 0.3)',
                                color: '#60A5FA',
                                padding: '0.35rem 0.7rem',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontSize: '0.75rem',
                                fontWeight: 600
                              }}
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => setDeletingStudent(s)}
                              style={{
                                background: 'rgba(239, 68, 68, 0.15)',
                                border: '1px solid rgba(239, 68, 68, 0.3)',
                                color: '#F87171',
                                padding: '0.35rem 0.7rem',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontSize: '0.75rem',
                                fontWeight: 600
                              }}
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
        )}

        {/* TAB 3: REPORTS & ANALYTICS */}
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

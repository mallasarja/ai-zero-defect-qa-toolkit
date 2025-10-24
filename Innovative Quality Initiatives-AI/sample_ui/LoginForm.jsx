import React, { useState, useId } from 'react';

// Accessible Login Form sample component (for test generation context)
// Includes: labeled inputs, described-by help text, validation state, aria-live errors,
// keyboard-focusable controls, and proper button semantics.

export default function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [errors, setErrors] = useState({ email: '', password: '' });
  const [status, setStatus] = useState('');

  const emailId = useId();
  const emailHelpId = useId();
  const emailErrId = useId();
  const pwdId = useId();
  const pwdHelpId = useId();
  const pwdErrId = useId();
  const statusId = useId();

  function validate() {
    const next = { email: '', password: '' };
    if (!email) next.email = 'Email is required.';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) next.email = 'Enter a valid email.';
    if (!password) next.password = 'Password is required.';
    else if (password.length < 8) next.password = 'Password must be at least 8 characters.';
    setErrors(next);
    return !next.email && !next.password;
  }

  function onSubmit(e) {
    e.preventDefault();
    setStatus('');
    if (!validate()) {
      setStatus('Please fix the errors below.');
      return;
    }
    // Simulate submit
    setTimeout(() => {
      setStatus('Signed in successfully.');
    }, 300);
  }

  return (
    <div className="login-form-container" style={{ maxWidth: 400 }}>
      <h1>Sign in</h1>
      <p id={statusId} role="status" aria-live="polite" style={{ minHeight: 20 }}>
        {status}
      </p>
      <form onSubmit={onSubmit} noValidate aria-describedby={status ? statusId : undefined}>
        <div className="form-field">
          <label htmlFor={emailId}>Email address</label>
          <input
            id={emailId}
            name="email"
            type="email"
            inputMode="email"
            autoComplete="username"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            aria-required="true"
            aria-invalid={errors.email ? 'true' : 'false'}
            aria-describedby={`${emailHelpId}${errors.email ? ' ' + emailErrId : ''}`}
          />
          <div id={emailHelpId} className="help-text">Use your work email (e.g., user@example.com).</div>
          {errors.email && (
            <div id={emailErrId} className="error-text" role="alert">
              {errors.email}
            </div>
          )}
        </div>

        <div className="form-field">
          <label htmlFor={pwdId}>Password</label>
          <input
            id={pwdId}
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            aria-required="true"
            aria-invalid={errors.password ? 'true' : 'false'}
            aria-describedby={`${pwdHelpId}${errors.password ? ' ' + pwdErrId : ''}`}
          />
          <div id={pwdHelpId} className="help-text">Minimum 8 characters.</div>
          {errors.password && (
            <div id={pwdErrId} className="error-text" role="alert">
              {errors.password}
            </div>
          )}
        </div>

        <div className="form-row" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            id="rememberMe"
            name="rememberMe"
            type="checkbox"
            checked={remember}
            onChange={(e) => setRemember(e.target.checked)}
          />
          <label htmlFor="rememberMe">Remember me</label>
        </div>

        <div className="form-actions" style={{ marginTop: 16, display: 'flex', gap: 12 }}>
          <button type="submit">Sign in</button>
          <a href="#forgot" aria-label="Forgot your password?">Forgot password</a>
        </div>
      </form>

      <style>{`
        .form-field { margin-bottom: 12px; }
        label { display: block; font-weight: 600; margin-bottom: 4px; }
        input[type="email"], input[type="password"] { width: 100%; padding: 8px; }
        .help-text { font-size: 12px; color: #555; }
        .error-text { color: #b00020; font-size: 12px; margin-top: 4px; }
        button { padding: 8px 12px; }
      `}</style>
    </div>
  );
}


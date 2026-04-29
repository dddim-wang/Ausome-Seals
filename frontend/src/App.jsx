import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ShieldCheck,
  Factory,
  Wrench,
  Droplets,
  Gauge,
  Mail,
  Phone,
  MapPin,
  ArrowRight,
  CheckCircle2,
} from "lucide-react";
import logo from "./assets/logo.png";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

const products = [
  {
    title: "Hydraulic Gate Seals",
    desc: "High-strength sealing components for hydraulic gate systems used in steel production lines.",
    features: ["Pressure-resistant", "Wear-resistant", "Custom dimensions"],
  },
  {
    title: "Cylinder & Rod Seals",
    desc: "Precision seals for hydraulic cylinders, rods, and heavy-duty industrial motion systems.",
    features: ["Stable performance", "Low leakage", "Long service life"],
  },
  {
    title: "Guide Rings & Wipers",
    desc: "Supporting seal components for alignment, contamination control, and system protection.",
    features: ["Reduced friction", "Dust protection", "Reliable guidance"],
  },
];

const applications = [
  "Steel rolling mills",
  "Galvanizing lines",
  "Pickling lines",
  "Hydraulic gate equipment",
  "Heavy-duty industrial cylinders",
  "High-temperature production environments",
];

function Header() {
  return (
    <header className="site-header">
      <div className="container nav">
        <div className="brand">
          <img src={logo} alt="Ausome logo" className="brand-logo" />
          <div>
            <strong>Seals Technology</strong>
            <span>Industrial Sealing Solutions</span>
          </div>
        </div>
        <nav>
          <a href="#products">Products</a>
          <a href="#applications">Applications</a>
          <a href="#about">About</a>
          <a href="#contact" className="nav-cta">Contact</a>
        </nav>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="hero">
      <div className="container hero-grid">
        <div className="hero-copy">
          <div className="eyebrow">
            <ShieldCheck size={18} />
            Professional sealing solutions for steel industry hydraulics
          </div>
          <h1>Sealing products for demanding steel production systems.</h1>
          <p>
            Ausome Seals Technology provides industrial sealing solutions for
            hydraulic gate systems, cylinders, and heavy-duty steel production
            equipment. We focus on durability, leakage control, and dependable
            performance in challenging operating conditions.
          </p>
          <div className="hero-actions">
            <a href="#products" className="btn primary">
              View Products <ArrowRight size={18} />
            </a>
            <a href="#contact" className="btn secondary">Request a Quote</a>
          </div>
          <div className="stats">
            <div><strong>Steel</strong><span>Industry Focus</span></div>
            <div><strong>Custom</strong><span>Seal Design</span></div>
            <div><strong>B2B</strong><span>Technical Support</span></div>
          </div>
        </div>

        <div className="hero-card">
          <img src={logo} alt="Ausome logo" className="hero-logo" />
          <div className="diagram">
            <div className="gate gate-top"></div>
            <div className="seal-ring"></div>
            <div className="gate gate-bottom"></div>
          </div>
          <h3>Built for harsh production conditions</h3>
          <p>
            Designed for hydraulic equipment exposed to pressure cycling,
            abrasive environments, oil contamination, and continuous operation.
          </p>
        </div>
      </div>
    </section>
  );
}

function ProductSection() {
  return (
    <section id="products" className="section">
      <div className="container">
        <div className="section-head">
          <span>Product Portfolio</span>
          <h2>Industrial seals engineered for uptime</h2>
          <p>
            Core products can be adapted by material, profile, diameter,
            operating pressure, and equipment interface.
          </p>
        </div>

        <div className="cards">
          {products.map((item) => (
            <article className="product-card" key={item.title}>
              <div className="icon-box"><Droplets size={26} /></div>
              <h3>{item.title}</h3>
              <p>{item.desc}</p>
              <ul>
                {item.features.map((f) => (
                  <li key={f}><CheckCircle2 size={16} />{f}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function ApplicationSection() {
  return (
    <section id="applications" className="section muted">
      <div className="container split">
        <div>
          <div className="section-head left">
            <span>Applications</span>
            <h2>For steel manufacturing and heavy hydraulic equipment</h2>
            <p>
              Our sealing products are suitable for demanding hydraulic gate and
              cylinder applications across steel processing operations.
            </p>
          </div>
          <div className="application-grid">
            {applications.map((item) => <div key={item}>{item}</div>)}
          </div>
        </div>

        <div className="capability-panel">
          <Factory size={34} />
          <h3>Engineering capability</h3>
          <p>
            Support for seal selection, sample development, replacement
            matching, and application-specific product recommendations.
          </p>
          <div className="capability-row">
            <Gauge />
            <span>Pressure and operating condition review</span>
          </div>
          <div className="capability-row">
            <Wrench />
            <span>Custom sizing and profile adaptation</span>
          </div>
        </div>
      </div>
    </section>
  );
}

function AboutSection() {
  return (
    <section id="about" className="section dark">
      <div className="container about-grid">
        <div>
          <span className="section-tag">About Ausome</span>
          <h2>Focused on practical sealing performance for industrial clients.</h2>
        </div>
        <p>
          Ausome Seals Technology serves steel production and heavy industrial
          customers with hydraulic sealing products developed for durability,
          stable operation, and maintainability. We help customers reduce leakage
          risk, extend equipment service intervals, and improve system reliability.
        </p>
      </div>
    </section>
  );
}

function ContactSection() {
  const [status, setStatus] = useState("");
  const [form, setForm] = useState({
    name: "",
    company: "",
    email: "",
    message: "",
  });

  const update = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setStatus("Sending...");
    try {
      const res = await fetch(`${API_BASE}/api/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error("Request failed");
      setStatus("Message received. We will contact you soon.");
      setForm({ name: "", company: "", email: "", message: "" });
    } catch {
      setStatus("Unable to send right now. Please check backend connection.");
    }
  }

  return (
    <section id="contact" className="section">
      <div className="container contact-grid">
        <div>
          <div className="section-head left">
            <span>Contact</span>
            <h2>Request technical consultation or quotation</h2>
            <p>
              Send your equipment type, seal dimensions, operating pressure,
              temperature, medium, and quantity requirement.
            </p>
          </div>
          <div className="contact-info">
            <p><Mail size={18} /> ausomeseals@gmail.com</p>
            <p><Phone size={18} /> +86-137-7661-6519</p>
            <p><MapPin size={18} /> China / Global Industrial Customers</p>
          </div>
        </div>

        <form className="contact-form" onSubmit={submit}>
          <input name="name" placeholder="Your name" value={form.name} onChange={update} required />
          <input name="company" placeholder="Company" value={form.company} onChange={update} />
          <input name="email" type="email" placeholder="Email" value={form.email} onChange={update} required />
          <textarea name="message" placeholder="Tell us about your sealing requirement" value={form.message} onChange={update} required />
          <button className="btn primary" type="submit">Submit Inquiry</button>
          {status && <p className="form-status">{status}</p>}
        </form>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer>
      <div className="container footer-content">
        <div className="footer-brand">
          <img src={logo} alt="Ausome logo" className="footer-logo" />
          <div>
            <strong> Ausome Seals Technology</strong>
            <span>Industrial Sealing Solutions</span>
          </div>
        </div>
        <span>© {new Date().getFullYear()} Ausome Seals Technology. All rights reserved.</span>
      </div>
    </footer>
  );
}

function App() {
  return (
    <>
      <Header />
      <Hero />
      <ProductSection />
      <ApplicationSection />
      <AboutSection />
      <ContactSection />
      <Footer />
    </>
  );
}

createRoot(document.getElementById("root")).render(<App />);

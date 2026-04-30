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
  Menu,
  X,
} from "lucide-react";

import logo from "./assets/logo.png";
import "./styles.css";

import product1 from "./assets/products/product1.jpg";
import product2 from "./assets/products/product2.jpg";
import product3 from "./assets/products/product3.jpg";

import factory1 from "./assets/factory/factory1.jpg";
import factory2 from "./assets/factory/factory2.jpg";
import factory3 from "./assets/factory/factory3.jpg";

import coop1 from "./assets/coop/coop1.png";
import coop2 from "./assets/coop/coop2.jpg";
import coop3 from "./assets/coop/coop3.jpg";
import coop4 from "./assets/coop/coop4.jpg";
import coop5 from "./assets/coop/coop5.jpg";
import coop6 from "./assets/coop/coop6.png";
import coop7 from "./assets/coop/coop7.png";
import coop8 from "./assets/coop/coop8.jpg";
import coop9 from "./assets/coop/coop9.jpg";
import coop10 from "./assets/coop/coop10.jpg";
import coop11 from "./assets/coop/coop11.jpg";
import coop12 from "./assets/coop/coop12.jpg";
import coop13 from "./assets/coop/coop13.jpg";
import coop14 from "./assets/coop/coop14.jpg";
import coop15 from "./assets/coop/coop15.jpg";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

const translations = {
  en: {
    brandName: "Seals Technology",
    brandSubtitle: "Industrial Sealing Solutions",

    navProducts: "Products",
    navApplications: "Applications",
    navCooperation: "Cooperation",
    navAbout: "About",
    navContact: "Contact",

    heroEyebrow: "Professional sealing solutions for steel industry hydraulics",
    heroTitle: "Sealing products for demanding steel production systems.",
    heroText:
      "Ausome Seals Technology provides industrial sealing solutions for hydraulic gate systems, cylinders, and heavy-duty steel production equipment. We focus on durability, leakage control, and dependable performance in challenging operating conditions.",
    viewProducts: "View Products",
    requestQuote: "Request a Quote",

    steel: "Steel",
    industryFocus: "Industry Focus",
    custom: "Custom",
    sealDesign: "Seal Design",
    b2b: "B2B",
    technicalSupport: "Technical Support",

    heroCardTitle: "Built for harsh production conditions",
    heroCardText:
      "Designed for hydraulic equipment exposed to pressure cycling, abrasive environments, oil contamination, and continuous operation.",

    factoryLabel: "Manufacturing",
    factoryTitle: "Production Environment & Factory Strength",
    factoryText:
      "Ausome Seals Technology focuses on industrial sealing solutions with reliable manufacturing capability, quality control, and technical support.",

    productsLabel: "Product Portfolio",
    productsTitle: "Industrial seals engineered for uptime",
    productsText:
      "Core products can be adapted by material, profile, diameter, operating pressure, and equipment interface.",

    applicationsLabel: "Applications",
    applicationsTitle: "For steel manufacturing and heavy hydraulic equipment",
    applicationsText:
      "Our sealing products are suitable for demanding hydraulic gate and cylinder applications across steel processing operations.",
    pressureReview: "Pressure and operating condition review",
    customSizing: "Custom sizing and profile adaptation",

    cooperationLabel: "Cooperation",
    cooperationTitle: "Trusted by industrial partners",
    cooperationText:
      "We support steel production, hydraulic equipment, and heavy industry customers with reliable sealing products and technical service.",

    aboutLabel: "About Ausome",
    aboutTitle: "Focused on practical sealing performance for industrial clients.",
    aboutText:
      "Ausome Seals Technology serves steel production and heavy industrial customers with hydraulic sealing products developed for durability, stable operation, and maintainability. We help customers reduce leakage risk, extend equipment service intervals, and improve system reliability.",

    contactLabel: "Contact",
    contactTitle: "Request technical consultation or quotation",
    contactText:
      "Send your equipment type, seal dimensions, operating pressure, temperature, medium, and quantity requirement.",
    namePlaceholder: "Your name",
    companyPlaceholder: "Company",
    emailPlaceholder: "Email",
    messagePlaceholder: "Tell us about your sealing requirement",
    submitInquiry: "Submit Inquiry",
    sending: "Sending...",
    successMessage: "Message received. We will contact you soon.",
    errorMessage: "Unable to send right now. Please check backend connection.",

    email: "ausomeseals@gmail.com",
    phone: "+86-137-7661-6519",
    location: "China / Global Industrial Customers",

    footerRights: "All rights reserved.",

    products: [
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
    ],

    applications: [
      "Steel rolling mills",
      "Galvanizing lines",
      "Pickling lines",
      "Hydraulic gate equipment",
      "Heavy-duty industrial cylinders",
      "High-temperature production environments",
    ],
  },

  zh: {
    brandName: "密封科技",
    brandSubtitle: "工业密封解决方案",

    navProducts: "产品",
    navApplications: "应用场景",
    navCooperation: "合作伙伴",
    navAbout: "关于我们",
    navContact: "联系我们",

    heroEyebrow: "面向钢铁行业液压系统的专业密封解决方案",
    heroTitle: "适用于严苛钢铁生产系统的密封产品。",
    heroText:
      "Ausome Seals Technology 为液压闸机系统、液压缸以及重型钢铁生产设备提供工业密封解决方案。我们专注于产品耐久性、泄漏控制以及复杂工况下的稳定运行表现。",
    viewProducts: "查看产品",
    requestQuote: "获取报价",

    steel: "钢铁",
    industryFocus: "行业专注",
    custom: "定制",
    sealDesign: "密封设计",
    b2b: "B2B",
    technicalSupport: "技术支持",

    heroCardTitle: "适用于严苛生产工况",
    heroCardText:
      "产品适用于承受压力循环、磨损环境、液压油污染以及连续运行要求的液压设备。",

    factoryLabel: "生产制造",
    factoryTitle: "生产环境与工厂实力",
    factoryText:
      "Ausome Seals Technology 专注于工业密封产品，具备可靠的制造能力、质量控制能力和技术支持能力。",

    productsLabel: "产品系列",
    productsTitle: "为设备稳定运行而设计的工业密封产品",
    productsText:
      "核心产品可根据材料、截面形式、尺寸、工作压力以及设备接口进行适配。",

    applicationsLabel: "应用场景",
    applicationsTitle: "服务于钢铁制造与重型液压设备",
    applicationsText:
      "我们的密封产品适用于钢铁加工中的液压闸机、液压缸以及其他严苛工况设备。",
    pressureReview: "工作压力与工况评估",
    customSizing: "定制尺寸与截面适配",

    cooperationLabel: "合作伙伴",
    cooperationTitle: "受到工业客户与合作伙伴信赖",
    cooperationText:
      "我们为钢铁生产、液压设备以及重工业客户提供可靠的密封产品和技术服务。",

    aboutLabel: "关于 Ausome",
    aboutTitle: "专注于工业客户实际工况下的密封性能。",
    aboutText:
      "Ausome Seals Technology 服务于钢铁生产及重工业客户，提供具备耐久性、稳定性和可维护性的液压密封产品，帮助客户降低泄漏风险、延长设备维护周期并提升系统可靠性。",

    contactLabel: "联系我们",
    contactTitle: "获取技术咨询或产品报价",
    contactText:
      "请提供设备类型、密封尺寸、工作压力、温度、介质以及采购数量需求。",
    namePlaceholder: "您的姓名",
    companyPlaceholder: "公司名称",
    emailPlaceholder: "邮箱",
    messagePlaceholder: "请描述您的密封产品需求",
    submitInquiry: "提交询盘",
    sending: "发送中...",
    successMessage: "信息已收到，我们会尽快与您联系。",
    errorMessage: "暂时无法发送，请检查后端连接。",

    email: "ausomeseals@gmail.com",
    phone: "+86-137-7661-6519",
    location: "中国 / 全球工业客户",

    footerRights: "版权所有。",

    products: [
      {
        title: "液压闸机密封件",
        desc: "适用于钢铁生产线液压闸机系统的高强度密封组件。",
        features: ["耐高压", "耐磨损", "支持定制尺寸"],
      },
      {
        title: "液压缸与活塞杆密封件",
        desc: "适用于液压缸、活塞杆和重型工业运动系统的精密密封件。",
        features: ["性能稳定", "低泄漏", "使用寿命长"],
      },
      {
        title: "导向环与防尘圈",
        desc: "用于导向、污染控制和系统保护的辅助密封组件。",
        features: ["降低摩擦", "防尘保护", "导向可靠"],
      },
    ],

    applications: [
      "钢铁轧制产线",
      "镀锌生产线",
      "酸洗生产线",
      "液压闸机设备",
      "重型工业液压缸",
      "高温生产环境",
    ],
  },
};

const productImages = [product1, product2, product3];

const coopImages = [
  coop1,
  coop2,
  coop3,
  coop4,
  coop5,
  coop6,
  coop7,
  coop8,
  coop9,
  coop10,
  coop11,
  coop12,
  coop13,
  coop14,
  coop15,
];

function Header({ t, toggleLanguage }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const closeMenu = () => setMobileMenuOpen(false);

  return (
    <header className="site-header">
      <div className="container nav">
        <div className="brand">
          <button
            className="logo-button"
            onClick={toggleLanguage}
            title="Switch language"
            type="button"
          >
            <img src={logo} alt="Ausome logo" className="brand-logo" />
          </button>

          <div>
            <strong>Seals Technology</strong>
            <span>{t.brandSubtitle}</span>
          </div>
        </div>

        <button
          className="mobile-menu-button"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle navigation menu"
          type="button"
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        <nav className={mobileMenuOpen ? "nav-links open" : "nav-links"}>
          <a href="#products" onClick={closeMenu}>
            {t.navProducts}
          </a>
          <a href="#applications" onClick={closeMenu}>
            {t.navApplications}
          </a>
          <a href="#cooperation" onClick={closeMenu}>
            {t.navCooperation}
          </a>
          <a href="#about" onClick={closeMenu}>
            {t.navAbout}
          </a>
          <a href="#contact" className="nav-cta" onClick={closeMenu}>
            {t.navContact}
          </a>
        </nav>
      </div>
    </header>
  );
}

function Hero({ t }) {
  return (
    <section className="hero">
      <div className="container hero-grid">
        <div className="hero-copy">
          <div className="eyebrow">
            <ShieldCheck size={18} />
            {t.heroEyebrow}
          </div>

          <h1>{t.heroTitle}</h1>
          <p>{t.heroText}</p>

          <div className="hero-actions">
            <a href="#products" className="btn primary">
              {t.viewProducts} <ArrowRight size={18} />
            </a>
            <a href="#contact" className="btn secondary">
              {t.requestQuote}
            </a>
          </div>

          <div className="stats">
            <div>
              <strong>{t.steel}</strong>
              <span>{t.industryFocus}</span>
            </div>
            <div>
              <strong>{t.custom}</strong>
              <span>{t.sealDesign}</span>
            </div>
            <div>
              <strong>{t.b2b}</strong>
              <span>{t.technicalSupport}</span>
            </div>
          </div>
        </div>

        <div className="hero-card">
          <img src={logo} alt="Ausome logo" className="hero-logo" />

          <div className="diagram">
            <div className="gate gate-top"></div>
            <div className="seal-ring"></div>
            <div className="gate gate-bottom"></div>
          </div>

          <h3>{t.heroCardTitle}</h3>
          <p>{t.heroCardText}</p>
        </div>
      </div>
    </section>
  );
}

function FactorySection({ t }) {
  return (
    <section className="section muted" id="factory">
      <div className="container">
        <div className="section-head">
          <span>{t.factoryLabel}</span>
          <h2>{t.factoryTitle}</h2>
          <p>{t.factoryText}</p>
        </div>

        <div className="factory-grid">
          <img src={factory1} alt="Factory 1" className="factory-image" />
          <img src={factory2} alt="Factory 2" className="factory-image" />
          <img src={factory3} alt="Factory 3" className="factory-image" />
        </div>
      </div>
    </section>
  );
}

function ProductSection({ t }) {
  return (
    <section id="products" className="section">
      <div className="container">
        <div className="section-head">
          <span>{t.productsLabel}</span>
          <h2>{t.productsTitle}</h2>
          <p>{t.productsText}</p>
        </div>

        <div className="cards">
          {t.products.map((item, index) => (
            <article className="product-card" key={item.title}>
              <img
                src={productImages[index]}
                alt={item.title}
                className="product-image"
              />

              <div className="icon-box">
                <Droplets size={26} />
              </div>

              <h3>{item.title}</h3>
              <p>{item.desc}</p>

              <ul>
                {item.features.map((feature) => (
                  <li key={feature}>
                    <CheckCircle2 size={16} />
                    {feature}
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function ApplicationSection({ t }) {
  return (
    <section id="applications" className="section muted">
      <div className="container split">
        <div>
          <div className="section-head left">
            <span>{t.applicationsLabel}</span>
            <h2>{t.applicationsTitle}</h2>
            <p>{t.applicationsText}</p>
          </div>

          <div className="application-grid">
            {t.applications.map((item) => (
              <div key={item}>{item}</div>
            ))}
          </div>
        </div>

        <div className="capability-panel">
          <Factory size={34} />
          <h3>{t.technicalSupport}</h3>
          <p>{t.applicationsText}</p>

          <div className="capability-row">
            <Gauge />
            <span>{t.pressureReview}</span>
          </div>

          <div className="capability-row">
            <Wrench />
            <span>{t.customSizing}</span>
          </div>
        </div>
      </div>
    </section>
  );
}

function CooperationSection({ t }) {
  const scrollingImages = [...coopImages, ...coopImages];

  return (
    <section id="cooperation" className="section cooperation-section">
      <div className="container">
        <div className="section-head">
          <span>{t.cooperationLabel}</span>
          <h2>{t.cooperationTitle}</h2>
          <p>{t.cooperationText}</p>
        </div>
      </div>

      <div className="coop-slider">
        <div className="coop-track">
          {scrollingImages.map((image, index) => (
            <div className="coop-card" key={`${image}-${index}`}>
              <img src={image} alt={`Cooperation partner ${index + 1}`} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function AboutSection({ t }) {
  return (
    <section id="about" className="section dark">
      <div className="container about-grid">
        <div>
          <span className="section-tag">{t.aboutLabel}</span>
          <h2>{t.aboutTitle}</h2>
        </div>

        <p>{t.aboutText}</p>
      </div>
    </section>
  );
}

function ContactSection({ t }) {
  const [status, setStatus] = useState("");
  const [form, setForm] = useState({
    name: "",
    company: "",
    email: "",
    message: "",
  });

  const update = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value });
  };

  async function submit(event) {
    event.preventDefault();
    setStatus(t.sending);

    try {
      const response = await fetch(`${API_BASE}/api/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        throw new Error("Request failed");
      }

      setStatus(t.successMessage);
      setForm({
        name: "",
        company: "",
        email: "",
        message: "",
      });
    } catch {
      setStatus(t.errorMessage);
    }
  }

  return (
    <section id="contact" className="section">
      <div className="container contact-grid">
        <div>
          <div className="section-head left">
            <span>{t.contactLabel}</span>
            <h2>{t.contactTitle}</h2>
            <p>{t.contactText}</p>
          </div>

          <div className="contact-info">
            <p>
              <Mail size={18} /> {t.email}
            </p>
            <p>
              <Phone size={18} /> {t.phone}
            </p>
            <p>
              <MapPin size={18} /> {t.location}
            </p>
          </div>
        </div>

        <form className="contact-form" onSubmit={submit}>
          <input
            name="name"
            placeholder={t.namePlaceholder}
            value={form.name}
            onChange={update}
            required
          />

          <input
            name="company"
            placeholder={t.companyPlaceholder}
            value={form.company}
            onChange={update}
          />

          <input
            name="email"
            type="email"
            placeholder={t.emailPlaceholder}
            value={form.email}
            onChange={update}
            required
          />

          <textarea
            name="message"
            placeholder={t.messagePlaceholder}
            value={form.message}
            onChange={update}
            required
          />

          <button className="btn primary" type="submit">
            {t.submitInquiry}
          </button>

          {status && <p className="form-status">{status}</p>}
        </form>
      </div>
    </section>
  );
}

function Footer({ t }) {
  return (
    <footer>
      <div className="container footer-content">
        <div className="footer-brand">
          <img src={logo} alt="Ausome logo" className="footer-logo" />

          <div>
            <strong>Ausome Seals Technology</strong>
            <span>{t.brandSubtitle}</span>
          </div>
        </div>

        <span>
          © {new Date().getFullYear()} Ausome Seals Technology. {t.footerRights}
        </span>
      </div>
    </footer>
  );
}

function App() {
  const [lang, setLang] = useState("en");

  const toggleLanguage = () => {
    setLang((current) => (current === "en" ? "zh" : "en"));
  };

  const t = translations[lang];

  return (
    <>
      <Header t={t} toggleLanguage={toggleLanguage} />
      <Hero t={t} />
      <FactorySection t={t} />
      <ProductSection t={t} />
      <ApplicationSection t={t} />
      <CooperationSection t={t} />
      <AboutSection t={t} />
      <ContactSection t={t} />
      <Footer t={t} />
    </>
  );
}

createRoot(document.getElementById("root")).render(<App />);
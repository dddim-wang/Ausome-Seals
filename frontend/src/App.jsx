import React, { useState, useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";
import {
  ShieldCheck,
  Factory,
  Droplets,
  Mail,
  Phone,
  MapPin,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  Download,
  Menu,
  X,
} from "lucide-react";

import logo from "./assets/logo.webp";
import "./styles.css";
import ChatWidget from "./ChatWidget";

import product1 from "./assets/products/product1.webp";
import product2 from "./assets/products/product2.webp";
import product3 from "./assets/products/product3.webp";

// Factory images
import factory1 from "./assets/factory/factory1.webp";
import factory2 from "./assets/factory/factory2.webp";
import factory3 from "./assets/factory/factory3.webp";
import factory4 from "./assets/factory/factory4.webp";
import factory5 from "./assets/factory/factory5.webp";
import factory6 from "./assets/factory/factory6.webp";
import factory7 from "./assets/factory/factory7.webp";
import factory8 from "./assets/factory/factory8.webp";
import factory9 from "./assets/factory/factory9.webp";

// Lab images
import lab1 from "./assets/factory/lab1.webp";
import lab2 from "./assets/factory/lab2.webp";
import lab3 from "./assets/factory/lab3.webp";


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

const API_BASE = (import.meta.env.VITE_API_BASE || "").replace(/\/$/, "");
const imagePreloadCache = new Map();

function preloadImage(src) {
  if (!imagePreloadCache.has(src)) {
    const image = new Image();
    image.decoding = "async";
    image.src = src;
    imagePreloadCache.set(src, image);
  }

  return imagePreloadCache.get(src);
}

const translations = {
  en: {
    brandName: "Ausome Seals",
    brandSubtitle: "Heavy Machinery Sealing Solutions",
    seoTitle: "Ausome Seals | Heavy Machinery Sealing Solutions",
    seoDescription: "Custom oil seals and rubber sealing products for steel mills, heavy machinery, cylinders, pumps, gearboxes, and industrial equipment.",
    openMenu: "Open navigation menu",
    closeMenu: "Close navigation menu",
    previousImage: "Previous image",
    nextImage: "Next image",
    navProducts: "Products",
    navApplications: "Applications",
    navCooperation: "Partners",
    navAbout: "About",
    navContact: "Contact",
    heroEyebrow: "Custom sealing solutions for heavy machinery and industrial hydraulics",
    heroTitle: "Heavy Machinery Sealing Solutions.",
    heroText: "Ausome Seals provides sealing solutions across various industrial applications through its expertise in leakage control and custom sealing design. Our product lineup includes oil seals and other rubber-based sealing products for steel mills, heavy machinery, cylinders, pumps, gearboxes, and demanding production equipment.",
    viewProducts: "View Products",
    requestQuote: "Request a Quote",
    steel: "Heavy Machinery",
    industryFocus: "Industry Focus",
    custom: "Custom",
    sealDesign: "Seal Design",
    technicalSupport: "Technical Support",
    supportItems: ["Seal installation", "Replacement review", "Working-condition analysis"],
    heroCardTitle: "Custom-fit sealing",
    heroCardText: "From sample-based replacement to drawing-based production, we support maintenance teams with seals matched to real equipment positions, dimensions, materials, and working conditions.",

    factoryTitle: "Manufacturing",
    factoryText: "Based in Nanjing, China, our factory operates multiple oil seal production lines with high-specification equipment, experienced rubber sealing specialists, and professional storage for stable quality control.",

    labTitle: "Testing",
    labText: "Testing and inspection support material selection, dimensional consistency, and reliable performance in high-pressure, abrasive, and oil-contaminated service conditions.",

    productsLabel: "Products",
    productsText: "Core products can be customized by material, profile, diameter, pressure, temperature, medium, and equipment interface.",
    catalogDownloadsLabel: "Product Catalog",
    catalogDownloadCn: "Chinese Catalog",
    catalogDownloadEn: "English Catalog",

    applicationsLabel: "Applications",
    applicationsText: "Beyond supplying sealing products, we provide technical support for seal installation, equipment operation, replacement review, and working-condition analysis to help maintenance teams improve reliability and reduce downtime risk.",

    cooperationLabel: "Partners",
    cooperationText: "Our products are used in rolling mill equipment across large steel plants in China, serving both private and state-owned enterprises. We are also expanding into more industrial sectors, providing sealing solutions for overseas equipment builders, heavy machinery users, and maintenance partners.",

    aboutLabel: "About",
    aboutTitle: "Built for Demanding Conditions.",
    aboutText: "Based in China, Ausome Seals is a sealing product manufacturer with years of experience in heavy equipment sealing applications for steel plants. Through long-term cooperation with equipment users, maintenance teams, and manufacturing partners, we have built practical technical knowledge in seal selection, replacement, installation, and on-site application support. We are now bringing this manufacturing experience and service capability to international industrial customers.",

    contactLabel: "Contact",
    contactTitle: "Request a Quote",
    contactText: "Check the catalog for model and size guide, or send us your size, conditions, application, or sample photo.",
    nameLabel: "Name",
    companyLabel: "Company",
    emailLabel: "Email",
    messageLabel: "Seal requirements",
    namePlaceholder: "Your name",
    companyPlaceholder: "Company",
    emailPlaceholder: "Email",
    messagePlaceholder: "Size, conditions, application, sample photo",
    submitInquiry: "Submit",
    sending: "Sending...",
    successMessage: "Message sent. We will contact you soon.",
    errorMessage: "Unable to send right now. Please try again later or contact us by email.",

    email: "support@ausomeseals.com",
    phone: "WhatsApp: +86 137-7661-6519",
    location: "China / Global Customers",
    footerRights: "All rights reserved.",

    products: [
  {
    title: "Oil Seal",
    desc: "Large oil seals for rolling mill roll bearing areas in steel plants. For more models and sizes, please download and review our product catalog.",
    features: ["Abrasive-resistant", "High-temperature resistant", "Drawing-based", "Custom profiles"],
  },
  {
    title: "Hydraulic & Cylinder Seals",
    desc: "Precision seals for hydraulic equipment, cylinders, rods, pistons, and heavy-duty motion systems in industrial production lines.",
    features: ["Pressure-resistant", "Low leakage", "Long service life"],
  },
  {
    title: "Guide Rings, Wipers & Wear Parts",
    desc: "Supporting components for alignment, contamination control, dust protection, and system protection in harsh machinery environments.",
    features: ["Reduced friction", "Scale protection", "Reliable guidance"],
  },
],
    applications: [
  "Heavy machinery and production equipment",
  "Bearing housings and rotating equipment",
  "Hydraulic equipment and cylinders",
  "Mill stands and bearing areas",
  "Mining, metallurgy, and material handling equipment",
  "Hydraulic gate equipment",
],
  },

  zh: {
    brandName: "Ausome Seals",
    brandSubtitle: "重型机械密封解决方案",
    seoTitle: "Ausome Seals | 重型机械密封解决方案",
    seoDescription: "为钢铁厂、重型机械、液压缸、泵、齿轮箱和工业设备提供定制油封与橡胶密封产品。",
    openMenu: "打开导航菜单",
    closeMenu: "关闭导航菜单",
    previousImage: "上一张图片",
    nextImage: "下一张图片",
    navProducts: "产品",
    navApplications: "应用场景",
    navCooperation: "合作伙伴",
    navAbout: "关于我们",
    navContact: "联系我们",
    heroEyebrow: "面向重型机械与工业液压系统的定制密封",
    heroTitle: "重型机械密封解决方案。",
    heroText: "Ausome Seals 凭借泄漏控制和定制密封设计经验，为多类工业应用提供密封解决方案。产品包括油封以及其他橡胶类密封产品，适用于钢厂、重型机械、液压缸、泵、齿轮箱和严苛工况生产设备。",
    viewProducts: "查看产品",
    requestQuote: "获取报价",
    steel: "重型机械",
    industryFocus: "行业专注",
    custom: "定制",
    sealDesign: "密封设计",
    technicalSupport: "技术支持",
    supportItems: ["密封安装", "替换评估", "工况分析"],
    heroCardTitle: "定制适配密封",
    heroCardText: "支持来样替换、按图加工和工况确认，帮助设备检修团队根据设备位置、尺寸、材料和实际工况匹配合适的密封件。",

    factoryTitle: "生产制造",
    factoryText: "我们的工厂位于中国南京，配备多条油封生产线，均采用高规格生产设备。生产环节由多位拥有十余年橡胶密封件制造经验的资深人员指导，并配套专业仓储环境，保障产品质量稳定。",

    labTitle: "测试设施",
    labText: "测试与检验能力支持材料选择、尺寸一致性以及高压、磨损、油污等工况下的可靠表现。",

    productsLabel: "产品系列",
    productsText: "核心产品可根据材料、截面形式、直径、压力、温度、介质以及设备接口进行定制。",
    catalogDownloadsLabel: "\u4ea7\u54c1\u624b\u518c",
    catalogDownloadCn: "\u4e2d\u6587\u624b\u518c",
    catalogDownloadEn: "\u82f1\u6587\u624b\u518c",

    applicationsLabel: "应用场景",
    applicationsText: "我们不仅提供密封产品，也为客户提供产品安装、设备运行、替换评估和工况分析等技术服务支持，帮助检修团队提升设备可靠性并降低停机风险。",

    cooperationLabel: "合作伙伴",
    cooperationText: "我们的产品已应用于中国各类大型钢铁厂轧机设备，客户覆盖民营企业与国有企业。我们也正向更多工业领域拓展，为海外设备制造商、重型机械用户和工业检修合作伙伴提供密封解决方案。",

    aboutLabel: "关于",
    aboutTitle: "面向严苛工况。",
    aboutText: "Ausome Seals是一家位于中国的密封产品制造企业，多年来专注于钢厂重型设备密封应用。通过与设备使用方、检修团队和制造合作伙伴的长期合作，我们积累了丰富的密封选型、替换、安装和现场应用技术经验。现在，我们正将这些制造经验与服务能力带向国际工业客户。",

    contactLabel: "联系我们",
    contactTitle: "获取报价",
    contactText: "请先查看产品目录中的型号与尺寸指南，或发送所需尺寸、工况、使用场景或样品图片。",
    nameLabel: "姓名",
    companyLabel: "公司",
    emailLabel: "邮箱",
    messageLabel: "密封需求",
    namePlaceholder: "您的姓名",
    companyPlaceholder: "公司名称",
    emailPlaceholder: "邮箱",
    messagePlaceholder: "尺寸、工况、使用场景、样品图片",
    submitInquiry: "提交",
    sending: "发送中...",
    successMessage: "消息已发送，我们会尽快与您联系。",
    errorMessage: "暂时无法发送，请稍后重试或通过邮箱联系我们。",

    email: "support@ausomeseals.com",
    phone: "WhatsApp: +86 137-7661-6519",
    location: "中国 / 全球客户",
    footerRights: "版权所有。",

    products: [
      {
        title: "重型机械密封件",
        desc: "图例为大型油封，适用于钢铁厂轧机轧辊轴承区域。更多型号和尺寸，请下载查看产品目录。",
        features: ["耐磨污染", "耐高温", "按图加工", "定制截面"],
      },
      {
        title: "液压系统与液压缸密封件",
        desc: "适用于工业液压设备、液压缸、活塞杆、活塞和重载运动系统的精密密封件。",
        features: ["耐高压", "低泄漏", "寿命稳定"],
      },
      {
        title: "导向环、防尘圈与耐磨件",
        desc: "用于严苛机械环境中的导向、污染控制、防尘保护和系统防护的辅助组件。",
        features: ["降低摩擦", "防磨粒污染", "导向可靠"],
      },
    ],

    applications: [
      "重型机械与生产设备",
      "轴承座与旋转设备",
      "工业液压设备与液压缸",
      "轧机机架与轴承区域",
      "矿山、冶金与物料搬运设备",
      "液压闸机设备",
    ],
  },
};

const productImages = [product3, product1, product2];
const catalogCn = "/catalogs/Ausome_Seals_Oil_Seal_Catalog_CN.pdf";
const catalogEn = "/catalogs/Ausome_Seals_Oil_Seal_Catalog_EN.pdf";

const factoryImages = [factory1, factory2, factory3, factory4, factory5, factory6, factory7, factory8, factory9];
const labImages = [lab1, lab2, lab3];

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

function Header({ t, mobileMenuOpen, setMobileMenuOpen }) {
  return (
    <header className="site-header">
      <div className="container nav">
        <div className="brand">
          <img
            src={logo}
            alt="Ausome logo"
            className="brand-logo"
            loading="eager"
            fetchPriority="high"
          />
          <div>
            <strong>{t.brandName}</strong>
            <span>{t.brandSubtitle}</span>
          </div>
        </div>

        <button
          className="mobile-menu-button"
          onClick={() => setMobileMenuOpen((open) => !open)}
          aria-label={mobileMenuOpen ? t.closeMenu : t.openMenu}
          aria-controls="mobile-navigation"
          aria-expanded={mobileMenuOpen}
          type="button"
        >
          {mobileMenuOpen ? (
            <X size={19} strokeWidth={1.8} />
          ) : (
            <Menu size={19} strokeWidth={1.8} />
          )}
        </button>

        <nav className="desktop-nav-links">
          <a href="#products">{t.navProducts}</a>
          <a href="#applications">{t.navApplications}</a>
          <a href="#cooperation">{t.navCooperation}</a>
          <a href="#about">{t.navAbout}</a>
          <a href="#contact" className="nav-cta">{t.navContact}</a>
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
          {t.heroText && <p>{t.heroText}</p>}

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

          </div>
        </div>

        <div className="hero-card">
          <img
            src={logo}
            alt="Ausome logo"
            className="hero-logo"
            loading="eager"
            fetchPriority="high"
          />

          <div className="diagram">
            <div className="gate gate-top"></div>
            <div className="seal-ring" aria-hidden="true" />
            <div className="gate gate-bottom"></div>
          </div>

          <h3>{t.heroCardTitle}</h3>
          <p>{t.heroCardText}</p>
        </div>
      </div>
    </section>
  );
}

function ProductSection({ t }) {
  const product = t.products[0];
  const sectionRef = useRef(null);
  const [currentImage, setCurrentImage] = useState(0);

  useEffect(() => {
    const section = sectionRef.current;
    if (!section) return undefined;

    const preloadImages = () => {
      productImages.forEach(preloadImage);
    };

    if (!("IntersectionObserver" in window)) {
      preloadImages();
      return undefined;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          preloadImages();
          observer.disconnect();
        }
      },
      { rootMargin: "300px" },
    );

    observer.observe(section);
    return () => observer.disconnect();
  }, []);

  const prevImage = () => {
    setCurrentImage((index) => (index - 1 + productImages.length) % productImages.length);
  };

  const nextImage = () => {
    setCurrentImage((index) => (index + 1) % productImages.length);
  };

  return (
    <section id="products" className="section" ref={sectionRef}>
      <div className="container">
        <div className="section-head section-head-label-only">
          <h2 className="section-label-title">{t.productsLabel}</h2>
          <p>{t.productsText}</p>
        </div>

        <div className="cards single-product">
          <article className="product-card featured-product" key={product.title}>
            <div className="product-carousel" aria-label={product.title}>
              <button className="product-carousel-btn prev" onClick={prevImage} type="button" aria-label={t.previousImage}>
                <ChevronLeft size={22} />
              </button>

              <img
                src={productImages[currentImage]}
                alt={product.title}
                className="product-image"
                loading="lazy"
                decoding="async"
              />

              <button className="product-carousel-btn next" onClick={nextImage} type="button" aria-label={t.nextImage}>
                <ChevronRight size={22} />
              </button>

              <div className="product-carousel-dots">
                {productImages.map((image, index) => (
                  <button
                    className={index === currentImage ? "active" : ""}
                    key={image}
                    onClick={() => setCurrentImage(index)}
                    type="button"
                    aria-label={`Show product image ${index + 1}`}
                  />
                ))}
              </div>
            </div>

            <div className="product-content">
              <div className="icon-box">
                <Droplets size={26} />
              </div>

              <h3>{product.title}</h3>
              <p>{product.desc}</p>

              <ul>
                {product.features.map((feature) => (
                  <li key={feature}>
                    <CheckCircle2 size={16} />
                    {feature}
                  </li>
                ))}
              </ul>

              <div className="catalog-downloads" aria-label={t.catalogDownloadsLabel}>
                <span>{t.catalogDownloadsLabel}</span>
                <div className="catalog-download-actions">
                  <a
                    className="btn catalog-download-btn"
                    href={catalogCn}
                    download="Ausome_Seals_Oil_Seal_Catalog_CN.pdf"
                    target="_blank"
                    rel="noreferrer"
                  >
                    <Download size={18} />
                    {t.catalogDownloadCn}
                  </a>
                  <a
                    className="btn catalog-download-btn"
                    href={catalogEn}
                    download="Ausome_Seals_Oil_Seal_Catalog_EN.pdf"
                    target="_blank"
                    rel="noreferrer"
                  >
                    <Download size={18} />
                    {t.catalogDownloadEn}
                  </a>
                </div>
              </div>
            </div>
          </article>
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
          <div className="section-head left section-head-label-only">
            <h2 className="section-label-title">{t.applicationsLabel}</h2>
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
          {t.supportItems.map((item) => (
            <div className="capability-row" key={item}>
              <CheckCircle2 size={20} />
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CooperationSection({ t }) {
  const sliderRef = useRef(null);
  const trackRef = useRef(null);
  const offsetRef = useRef(0);
  const setWidthRef = useRef(0);
  const lastPointerXRef = useRef(0);
  const lastMoveTimeRef = useRef(0);
  const velocityRef = useRef(0);
  const inertiaFrameRef = useRef(null);
  const isDraggingRef = useRef(false);
  const hasUserControlledRef = useRef(false);
  const [isDragging, setIsDragging] = useState(false);
  const scrollingImages = [...coopImages, ...coopImages, ...coopImages];

  useEffect(() => {
    const track = trackRef.current;
    if (!track) return;

    const applyOffset = () => {
      track.style.transform = `translate3d(${offsetRef.current}px, 0, 0)`;
    };

    const normalizeOffset = (value) => {
      const setWidth = setWidthRef.current;
      if (!setWidth) return value;

      let nextValue = value;
      while (nextValue <= -setWidth * 2) {
        nextValue += setWidth;
      }
      while (nextValue >= 0) {
        nextValue -= setWidth;
      }

      return nextValue;
    };

    const measure = () => {
      const firstSetCards = Array.from(track.children).slice(0, coopImages.length);
      const gap = parseFloat(window.getComputedStyle(track).columnGap || "0");
      const firstSetWidth = firstSetCards.reduce((total, card) => total + card.offsetWidth, 0) + gap * coopImages.length;

      setWidthRef.current = firstSetWidth;
      offsetRef.current = normalizeOffset(offsetRef.current || -firstSetWidth);
      applyOffset();
    };

    measure();
    window.addEventListener("resize", measure);

    let animationFrameId;

    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      let previousTime = performance.now();
      const speed = 36;

      const animate = (time) => {
        const elapsedSeconds = (time - previousTime) / 1000;
        previousTime = time;

        if (!hasUserControlledRef.current && !isDraggingRef.current) {
          offsetRef.current = normalizeOffset(offsetRef.current - speed * elapsedSeconds);
          applyOffset();
        }

        animationFrameId = requestAnimationFrame(animate);
      };

      animationFrameId = requestAnimationFrame(animate);
    }

    return () => {
      window.removeEventListener("resize", measure);
      cancelAnimationFrame(animationFrameId);
      cancelAnimationFrame(inertiaFrameRef.current);
    };
  }, []);

  const moveSliderBy = (deltaX) => {
    const track = trackRef.current;
    const setWidth = setWidthRef.current;
    if (!track || !setWidth) return;

    let nextOffset = offsetRef.current + deltaX;
    while (nextOffset <= -setWidth * 2) {
      nextOffset += setWidth;
    }
    while (nextOffset >= 0) {
      nextOffset -= setWidth;
    }

    offsetRef.current = nextOffset;
    track.style.transform = `translate3d(${offsetRef.current}px, 0, 0)`;
  };

  const startInertia = () => {
    cancelAnimationFrame(inertiaFrameRef.current);

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      velocityRef.current = 0;
      return;
    }

    let previousTime = performance.now();
    const friction = 0.92;
    const minimumVelocity = 8;

    const animateInertia = (time) => {
      const elapsedSeconds = Math.min((time - previousTime) / 1000, 0.04);
      previousTime = time;

      velocityRef.current *= friction;
      moveSliderBy(velocityRef.current * elapsedSeconds);

      if (Math.abs(velocityRef.current) > minimumVelocity && !isDraggingRef.current) {
        inertiaFrameRef.current = requestAnimationFrame(animateInertia);
      } else {
        velocityRef.current = 0;
        inertiaFrameRef.current = null;
      }
    };

    if (Math.abs(velocityRef.current) > minimumVelocity) {
      inertiaFrameRef.current = requestAnimationFrame(animateInertia);
    }
  };

  const startDragging = (event) => {
    cancelAnimationFrame(inertiaFrameRef.current);
    inertiaFrameRef.current = null;
    velocityRef.current = 0;
    hasUserControlledRef.current = true;
    isDraggingRef.current = true;
    lastPointerXRef.current = event.clientX;
    lastMoveTimeRef.current = performance.now();
    setIsDragging(true);
    sliderRef.current?.setPointerCapture?.(event.pointerId);
  };

  const dragSlider = (event) => {
    if (!isDraggingRef.current) return;

    const deltaX = event.clientX - lastPointerXRef.current;
    const now = performance.now();
    const elapsedSeconds = Math.max((now - lastMoveTimeRef.current) / 1000, 0.001);
    const instantVelocity = deltaX / elapsedSeconds;

    velocityRef.current = velocityRef.current * 0.55 + instantVelocity * 0.45;
    lastPointerXRef.current = event.clientX;
    lastMoveTimeRef.current = now;
    moveSliderBy(deltaX);
  };

  const stopDragging = (event) => {
    if (!isDraggingRef.current) return;

    isDraggingRef.current = false;
    setIsDragging(false);
    if (sliderRef.current?.hasPointerCapture?.(event.pointerId)) {
      sliderRef.current.releasePointerCapture(event.pointerId);
    }
    startInertia();
  };

  return (
    <section id="cooperation" className="section cooperation-section">
      <div className="container">
        <div className="section-head section-head-label-only">
          <h2 className="section-label-title">{t.cooperationLabel}</h2>
          <p>{t.cooperationText}</p>
        </div>
      </div>

      <div
        className={isDragging ? "coop-slider dragging" : "coop-slider"}
        ref={sliderRef}
        onPointerDown={startDragging}
        onPointerMove={dragSlider}
        onPointerUp={stopDragging}
        onPointerCancel={stopDragging}
        onLostPointerCapture={stopDragging}
      >
        <div className="coop-track" ref={trackRef}>
          {scrollingImages.map((image, index) => (
            <div className="coop-card" key={`${image}-${index}`}>
              <img
                src={image}
                alt=""
                loading="lazy"
                decoding="async"
                width="180"
                height="180"
              />
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
  const [statusKind, setStatusKind] = useState("info");
  const [isSending, setIsSending] = useState(false);
  const [form, setForm] = useState({
    name: "",
    company: "",
    email: "",
    message: "",
    website: "",
  });

  const update = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  async function submit(event) {
    event.preventDefault();
    if (isSending) return;

    setIsSending(true);
    setStatusKind("info");
    setStatus(t.sending);
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), 15000);

    try {
      const response = await fetch(`${API_BASE}/api/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error("Request failed");
      }

      setStatusKind("success");
      setStatus(t.successMessage);
      setForm({
        name: "",
        company: "",
        email: "",
        message: "",
        website: "",
      });
    } catch {
      setStatusKind("error");
      setStatus(t.errorMessage);
    } finally {
      window.clearTimeout(timeoutId);
      setIsSending(false);
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
              <Mail size={18} />
              <a href={"mailto:" + t.email}>{t.email}</a>
            </p>
            <p>
              <Phone size={18} />
              <a href="https://wa.me/8613776616519" target="_blank" rel="noreferrer">
                {t.phone}
              </a>
            </p>
            <p>
              <MapPin size={18} /> {t.location}
            </p>
          </div>
        </div>

        <form className="contact-form" onSubmit={submit}>
          <label htmlFor="contact-name">{t.nameLabel}</label>
          <input
            id="contact-name"
            name="name"
            autoComplete="name"
            placeholder={t.namePlaceholder}
            value={form.name}
            onChange={update}
            maxLength={120}
            required
          />

          <label htmlFor="contact-company">{t.companyLabel}</label>
          <input
            id="contact-company"
            name="company"
            autoComplete="organization"
            placeholder={t.companyPlaceholder}
            value={form.company}
            onChange={update}
            maxLength={200}
          />

          <label htmlFor="contact-email">{t.emailLabel}</label>
          <input
            id="contact-email"
            name="email"
            type="email"
            autoComplete="email"
            placeholder={t.emailPlaceholder}
            value={form.email}
            onChange={update}
            maxLength={254}
            required
          />

          <label htmlFor="contact-message">{t.messageLabel}</label>
          <textarea
            id="contact-message"
            name="message"
            placeholder={t.messagePlaceholder}
            value={form.message}
            onChange={update}
            maxLength={5000}
            required
          />

          <div className="honeypot" aria-hidden="true">
            <label htmlFor="contact-website">Website</label>
            <input
              id="contact-website"
              name="website"
              autoComplete="off"
              tabIndex={-1}
              value={form.website}
              onChange={update}
            />
          </div>

          <button className="btn primary" type="submit" disabled={isSending}>
            {isSending ? t.sending : t.submitInquiry}
          </button>

          {status && (
            <p
              className={"form-status " + statusKind}
              role={statusKind === "error" ? "alert" : "status"}
              aria-live="polite"
            >
              {status}
            </p>
          )}
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
            <strong>Ausome Seals</strong>
            <span>{t.brandSubtitle}</span>
          </div>
        </div>

        <span>
          © {new Date().getFullYear()} Ausome Seals. {t.footerRights}
        </span>
      </div>
    </footer>
  );
}

function LanguageToggle({ lang, toggleLanguage }) {
  return (
    <button
      className="language-toggle"
      onClick={toggleLanguage}
      type="button"
      aria-label="Switch language"
      title="Switch language"
    >
      {lang === "en" ? "中文" : "EN"}
    </button>
  );
}

function App() {
  const [lang, setLang] = useState("en");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleLanguage = () => {
    setLang((current) => (current === "en" ? "zh" : "en"));
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  const t = translations[lang];

  useEffect(() => {
    document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
    document.title = t.seoTitle;
    const description = document.querySelector('meta[name="description"]');
    description?.setAttribute("content", t.seoDescription);
  }, [lang, t.seoDescription, t.seoTitle]);

  useEffect(() => {
    if (!mobileMenuOpen) return undefined;

    const previousOverflow = document.body.style.overflow;
    const closeOnEscape = (event) => {
      if (event.key === "Escape") {
        setMobileMenuOpen(false);
      }
    };

    document.body.style.overflow = "hidden";
    document.body.classList.add("mobile-menu-open");
    window.addEventListener("keydown", closeOnEscape);

    return () => {
      document.body.style.overflow = previousOverflow;
      document.body.classList.remove("mobile-menu-open");
      window.removeEventListener("keydown", closeOnEscape);
    };
  }, [mobileMenuOpen]);

  return (
    <>
      {mobileMenuOpen && (
        <button
          className="menu-backdrop"
          onClick={closeMobileMenu}
          type="button"
          aria-label={t.closeMenu}
        />
      )}

      <nav
        id="mobile-navigation"
        className={mobileMenuOpen ? "mobile-nav-drawer open" : "mobile-nav-drawer"}
        aria-hidden={!mobileMenuOpen}
        inert={!mobileMenuOpen}
      >
        <a href="#products" onClick={closeMobileMenu}>{t.navProducts}</a>
        <a href="#applications" onClick={closeMobileMenu}>{t.navApplications}</a>
        <a href="#cooperation" onClick={closeMobileMenu}>{t.navCooperation}</a>
        <a href="#about" onClick={closeMobileMenu}>{t.navAbout}</a>
        <a href="#contact" className="nav-cta" onClick={closeMobileMenu}>{t.navContact}</a>
      </nav>

      <Header t={t} mobileMenuOpen={mobileMenuOpen} setMobileMenuOpen={setMobileMenuOpen} />
      <Hero t={t} />
      <ImageCarousel
        images={factoryImages}
        tTitle={t.factoryTitle}
        tText={t.factoryText}
        previousLabel={t.previousImage}
        nextLabel={t.nextImage}
      />

      <ImageCarousel
        images={labImages}
        tTitle={t.labTitle}
        tText={t.labText}
        previousLabel={t.previousImage}
        nextLabel={t.nextImage}
      />
      <ProductSection t={t} />
      <ApplicationSection t={t} />
      <CooperationSection t={t} />
      <AboutSection t={t} />
      <ContactSection t={t} />
      <Footer t={t} />
      <ChatWidget lang={lang} />
      <LanguageToggle lang={lang} toggleLanguage={toggleLanguage} />
    </>
  );
}

function ImageCarousel({ images, tTitle, tText, previousLabel, nextLabel }) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const priorityIndexes = [
      current,
      (current - 1 + images.length) % images.length,
      (current + 1) % images.length,
    ];

    priorityIndexes.forEach((index) => preloadImage(images[index]));
  }, [current, images]);

  useEffect(() => {
    let idleId;
    let timeoutId;

    const preloadRemaining = () => {
      const run = () => images.forEach(preloadImage);

      if ("requestIdleCallback" in window) {
        idleId = window.requestIdleCallback(run, { timeout: 2000 });
      } else {
        timeoutId = window.setTimeout(run, 250);
      }
    };

    if (document.readyState === "complete") {
      preloadRemaining();
    } else {
      window.addEventListener("load", preloadRemaining, { once: true });
    }

    return () => {
      window.removeEventListener("load", preloadRemaining);
      if (idleId !== undefined) window.cancelIdleCallback?.(idleId);
      if (timeoutId !== undefined) window.clearTimeout(timeoutId);
    };
  }, [images]);

  const prev = () => {
    setCurrent((index) => (index - 1 + images.length) % images.length);
  };

  const next = () => {
    setCurrent((index) => (index + 1) % images.length);
  };

  return (
    <section className="section muted carousel-section">
      <div className="container">
        <div className="section-head">
          <h2>{tTitle}</h2>
          <p>{tText}</p>
        </div>

        <div className="carousel-wrapper">
          <button className="carousel-btn prev" onClick={prev} type="button" aria-label={previousLabel}>
            &lt;
          </button>

          <img
            src={images[current]}
            alt={tTitle + " " + (current + 1)}
            className="carousel-image"
            loading="lazy"
            decoding="async"
          />

          <button className="carousel-btn next" onClick={next} type="button" aria-label={nextLabel}>
            &gt;
          </button>
        </div>
      </div>
    </section>
  );
}

createRoot(document.getElementById("root")).render(<App />);

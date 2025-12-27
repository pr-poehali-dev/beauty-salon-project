import HeroSection from "@/components/sections/HeroSection";
import ServicesSection from "@/components/sections/ServicesSection";
import GallerySection from "@/components/sections/GallerySection";
import ContactsSection from "@/components/sections/ContactsSection";
import BookingSection from "@/components/sections/BookingSection";

const Index = () => {
  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-white">
      <nav className="fixed top-0 left-0 right-0 bg-black/95 backdrop-blur-sm z-50 border-b border-gray-800">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold tracking-wide text-white">ProMissLab</h1>
              <img 
                src="https://cdn.poehali.dev/files/photo_2025-12-05_11-33-48.jpg" 
                alt="ProMissLab Logo" 
                className="h-12 w-auto"
              />
            </div>
            <div className="hidden md:flex gap-8 items-center">
              {["Главная", "Услуги", "Галерея", "Прайс", "Контакты", "Запись"].map((item) => (
                <button
                  key={item}
                  onClick={() => scrollToSection(item.toLowerCase())}
                  className="text-sm tracking-wider text-white hover:text-accent transition-colors relative group"
                >
                  {item.toUpperCase()}
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-accent group-hover:w-full transition-all duration-300"></span>
                </button>
              ))}
              <a 
                href="https://t.me/promisslab" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent/90 transition-all text-sm font-medium"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.295-.6.295-.002 0-.003 0-.005 0l.213-3.054 5.56-5.022c.24-.213-.054-.334-.373-.121l-6.869 4.326-2.96-.924c-.64-.203-.658-.64.135-.954l11.566-4.458c.538-.196 1.006.128.832.941z"/>
                </svg>
                TELEGRAM
              </a>
            </div>
          </div>
        </div>
      </nav>

      <HeroSection scrollToSection={scrollToSection} />
      <ServicesSection scrollToSection={scrollToSection} />
      <GallerySection />
      <ContactsSection />
      <BookingSection />

      <footer className="bg-black text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <p className="text-muted-foreground">© 2024 ProMissLab. Все права защищены.</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
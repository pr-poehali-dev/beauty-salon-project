import HeroSection from "@/components/sections/HeroSection";
import ServicesSection from "@/components/sections/ServicesSection";
import ContactsSection from "@/components/sections/ContactsSection";
import BookingSection from "@/components/sections/BookingSection";

const Index = () => {
  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-white">
      <nav className="fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-sm z-50 border-b border-gray-200">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-20">
            <button onClick={() => scrollToSection('главная')} className="flex items-center gap-3 hover:opacity-80 transition-opacity">
              <img 
                src="https://cdn.poehali.dev/files/photo_2025-12-05_11-33-48.jpg" 
                alt="ProMissLab" 
                className="h-12 w-auto"
              />
            </button>
            <div className="hidden md:flex gap-8">
              {["Главная", "Услуги", "Прайс", "Контакты", "Запись"].map((item) => (
                <button
                  key={item}
                  onClick={() => scrollToSection(item.toLowerCase())}
                  className="text-sm tracking-wider hover:text-accent transition-colors relative group"
                >
                  {item.toUpperCase()}
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-accent group-hover:w-full transition-all duration-300"></span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </nav>

      <HeroSection scrollToSection={scrollToSection} />
      <ServicesSection scrollToSection={scrollToSection} />
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
import { Button } from "@/components/ui/button";
import Icon from "@/components/ui/icon";

interface HeroSectionProps {
  scrollToSection: (id: string) => void;
}

const HeroSection = ({ scrollToSection }: HeroSectionProps) => {
  return (
    <section id="главная" className="pt-32 pb-20 px-4 bg-black">
      <div className="container mx-auto">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="animate-fade-in">
            <img 
              src="https://cdn.poehali.dev/files/Comp 1 (0;00;00;07)2.png" 
              alt="ProMissLab Logo" 
              className="w-96 mb-6"
            />
            <p className="text-accent text-sm tracking-widest mb-4">САЛОН КРАСОТЫ</p>
            <h2 className="text-6xl md:text-7xl font-bold mb-6 leading-tight text-white">
              Ваша красота —<br />наше искусство
            </h2>
            <p className="text-white text-lg mb-4 leading-relaxed">
              Профессиональные услуги красоты в элегантной атмосфере. 
              Более 20 видов услуг для вашего совершенства.
            </p>
            <a 
              href="https://yandex.ru/maps/?text=Санкт-Петербург, ул. Авиаконструкторов, 8Б" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-white hover:text-accent transition-colors mb-8 w-fit"
            >
              <Icon name="MapPin" size={20} className="text-accent" />
              <span>Санкт-Петербург, ул. Авиаконструкторов, 8Б</span>
            </a>
            <Button 
              size="lg" 
              className="bg-accent hover:bg-accent/90 text-black font-medium tracking-wider"
              onClick={() => scrollToSection("запись")}
            >
              ЗАПИСАТЬСЯ ОНЛАЙН
            </Button>
          </div>
          <div className="relative animate-slide-up">
            <img
              src="https://cdn.poehali.dev/projects/e2d9a565-7b30-444a-bbdf-46a6c01c8362/files/17718870-86f8-4dfe-9836-7c988d460af0.jpg"
              alt="Салон красоты"
              className="w-full h-[600px] object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
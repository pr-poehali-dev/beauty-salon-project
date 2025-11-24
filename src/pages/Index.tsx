import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import Icon from "@/components/ui/icon";
import { useToast } from "@/hooks/use-toast";

const Index = () => {
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    service: "",
    message: ""
  });
  const { toast } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast({
      title: "Заявка отправлена!",
      description: "Мы свяжемся с вами в ближайшее время",
    });
    setFormData({ name: "", phone: "", service: "", message: "" });
  };

  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  const services = [
    {
      category: "LPG",
      items: [
        { name: "30 минут", price: "1400 ₽" },
        { name: "40 минут", price: "1800 ₽" },
        { name: "60 минут", price: "2500 ₽" }
      ]
    },
    {
      category: "Ручной массаж тела",
      items: [
        { name: "Шейноворотниковый 30 минут", price: "2200 ₽" },
        { name: "Шейноворотниковый 45 минут", price: "2600 ₽" },
        { name: "Расслабляющий 1 час", price: "3200 ₽" },
        { name: "Расслабляющий 1,5 часа", price: "4200 ₽" },
        { name: "Антицеллюлитный 1 час", price: "3500 ₽" },
        { name: "Антицеллюлитный 75 минут", price: "4000 ₽" }
      ]
    },
    {
      category: "Вибро массаж",
      items: [
        { name: "20 минут", price: "1200 ₽" },
        { name: "30 минут", price: "1500 ₽" },
        { name: "40 минут", price: "1800 ₽" }
      ]
    },
    {
      category: "Массаж ручной лица",
      items: [
        { name: "30 минут", price: "1900 ₽" },
        { name: "45 минут", price: "2400 ₽" },
        { name: "60 минут", price: "2900 ₽" }
      ]
    },
    {
      category: "Чистка лица",
      items: [
        { name: "УЗ чистка", price: "1800 ₽" },
        { name: "Комбинированная", price: "от 2500 ₽" }
      ]
    },
    {
      category: "Кислотные пилинги",
      items: [
        { name: "Высокомолекулярные", price: "от 1800 ₽" },
        { name: "Серединные", price: "от 2500 ₽" },
        { name: "PRX 33", price: "от 4000 ₽" }
      ]
    },
    {
      category: "Уходовые процедуры по лицу",
      items: [
        { name: "Уходовая процедура", price: "от 1500 ₽" }
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <nav className="fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-sm z-50 border-b border-gray-200">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-20">
            <h1 className="text-3xl font-bold tracking-wide">ProMissLab</h1>
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

      <section id="главная" className="pt-32 pb-20 px-4">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="animate-fade-in">
              <p className="text-accent text-sm tracking-widest mb-4">ПРЕМИУМ САЛОН КРАСОТЫ</p>
              <h2 className="text-6xl md:text-7xl font-light mb-6 leading-tight">
                Ваша красота —<br />наше искусство
              </h2>
              <p className="text-muted-foreground text-lg mb-8 leading-relaxed">
                Профессиональные услуги красоты в элегантной атмосфере. 
                Более 20 видов услуг для вашего совершенства.
              </p>
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

      <section id="услуги" className="py-20 px-4 bg-secondary/30">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <p className="text-accent text-sm tracking-widest mb-4">НАШИ УСЛУГИ</p>
            <h2 className="text-5xl font-light">Спектр возможностей</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: "Sparkles", title: "Ногтевой сервис", desc: "Маникюр, педикюр, наращивание" },
              { icon: "Eye", title: "Брови и ресницы", desc: "Ламинирование, окрашивание, наращивание" },
              { icon: "Brush", title: "Перманентный макияж", desc: "Татуаж бровей, губ, век" },
              { icon: "Scissors", title: "Депиляция", desc: "Все виды эпиляции" },
              { icon: "Heart", title: "Уход за лицом", desc: "Чистка, биоревитализация, уходы" },
              { icon: "Waves", title: "Массаж и коррекция", desc: "LPG, лимфодренаж, прессотерапия" }
            ].map((service, idx) => (
              <Card key={idx} className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 group">
                <CardContent className="p-8 text-center">
                  <div className="w-16 h-16 mx-auto mb-6 bg-accent/10 rounded-full flex items-center justify-center group-hover:bg-accent/20 transition-colors">
                    <Icon name={service.icon} size={28} className="text-accent" />
                  </div>
                  <h3 className="text-2xl font-light mb-3">{service.title}</h3>
                  <p className="text-muted-foreground">{service.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section id="прайс" className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <p className="text-accent text-sm tracking-widest mb-4">ПРАЙС-ЛИСТ</p>
            <h2 className="text-5xl font-light">Стоимость услуг</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
            {services.map((category, idx) => (
              <Card key={idx} className="border border-gray-200 shadow-md">
                <CardContent className="p-8">
                  <h3 className="text-2xl font-light mb-6 pb-4 border-b border-accent/30">
                    {category.category}
                  </h3>
                  <div className="space-y-4">
                    {category.items.map((item, itemIdx) => (
                      <div key={itemIdx} className="flex justify-between items-start gap-4">
                        <span className="text-foreground">{item.name}</span>
                        <span className="text-accent font-medium whitespace-nowrap">{item.price}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 px-4 bg-black text-white">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-3 gap-12 text-center">
            <div>
              <div className="text-5xl font-light text-accent mb-4">100%</div>
              <p className="text-lg">Качество услуг</p>
            </div>
            <div>
              <div className="text-5xl font-light text-accent mb-4">2000+</div>
              <p className="text-lg">Довольных клиентов</p>
            </div>
            <div>
              <div className="text-5xl font-light text-accent mb-4">20+</div>
              <p className="text-lg">Видов услуг</p>
            </div>
          </div>
        </div>
      </section>

      <section id="контакты" className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <p className="text-accent text-sm tracking-widest mb-4">КОНТАКТЫ</p>
            <h2 className="text-5xl font-light">Где нас найти</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-12 max-w-5xl mx-auto">
            <div className="space-y-8">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0">
                  <Icon name="MapPin" size={24} className="text-accent" />
                </div>
                <div>
                  <h3 className="text-xl font-light mb-2">Адрес</h3>
                  <p className="text-muted-foreground">Санкт-Петербург<br />ул. Авиаконструкторов, 8Б</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0">
                  <Icon name="Phone" size={24} className="text-accent" />
                </div>
                <div>
                  <h3 className="text-xl font-light mb-2">Телефон</h3>
                  <p className="text-muted-foreground">+7 (812) 123-45-67</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0">
                  <Icon name="Clock" size={24} className="text-accent" />
                </div>
                <div>
                  <h3 className="text-xl font-light mb-2">Режим работы</h3>
                  <p className="text-muted-foreground">Ежедневно с 9:00 до 21:00</p>
                </div>
              </div>
            </div>
            <div className="h-[400px] bg-gray-200 rounded-lg overflow-hidden">
              <iframe
                src="https://yandex.ru/map-widget/v1/?ll=30.242916%2C60.011837&z=17&l=map&pt=30.242916,60.011837,pm2rdm"
                width="100%"
                height="100%"
                frameBorder="0"
                className="grayscale"
              ></iframe>
            </div>
          </div>
        </div>
      </section>

      <section id="запись" className="py-20 px-4 bg-secondary/30">
        <div className="container mx-auto max-w-2xl">
          <div className="text-center mb-12">
            <p className="text-accent text-sm tracking-widest mb-4">ОНЛАЙН ЗАПИСЬ</p>
            <h2 className="text-5xl font-light mb-4">Записаться на прием</h2>
            <p className="text-muted-foreground">Оставьте заявку и мы свяжемся с вами для подтверждения</p>
          </div>
          <Card className="border-0 shadow-xl">
            <CardContent className="p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <Label htmlFor="name" className="text-sm tracking-wider">ИМЯ</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    className="mt-2"
                    placeholder="Ваше имя"
                  />
                </div>
                <div>
                  <Label htmlFor="phone" className="text-sm tracking-wider">ТЕЛЕФОН</Label>
                  <Input
                    id="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    required
                    className="mt-2"
                    placeholder="+7 (___) ___-__-__"
                  />
                </div>
                <div>
                  <Label htmlFor="service" className="text-sm tracking-wider">УСЛУГА</Label>
                  <Input
                    id="service"
                    value={formData.service}
                    onChange={(e) => setFormData({ ...formData, service: e.target.value })}
                    required
                    className="mt-2"
                    placeholder="Например: Маникюр"
                  />
                </div>
                <div>
                  <Label htmlFor="message" className="text-sm tracking-wider">КОММЕНТАРИЙ</Label>
                  <Textarea
                    id="message"
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    className="mt-2 min-h-[100px]"
                    placeholder="Дополнительные пожелания"
                  />
                </div>
                <Button 
                  type="submit" 
                  size="lg" 
                  className="w-full bg-accent hover:bg-accent/90 text-black font-medium tracking-wider"
                >
                  ОТПРАВИТЬ ЗАЯВКУ
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>

      <footer className="bg-black text-white py-12 px-4">
        <div className="container mx-auto text-center">
          <h3 className="text-3xl font-light mb-4">ProMissLab</h3>
          <p className="text-gray-400 mb-6">Премиум салон красоты в Санкт-Петербурге</p>
          <div className="flex justify-center gap-6 mb-6">
            <a href="#" className="hover:text-accent transition-colors">
              <Icon name="Instagram" size={24} />
            </a>
            <a href="#" className="hover:text-accent transition-colors">
              <Icon name="Facebook" size={24} />
            </a>
            <a href="#" className="hover:text-accent transition-colors">
              <Icon name="Phone" size={24} />
            </a>
          </div>
          <p className="text-sm text-gray-500">© 2024 ProMissLab. Все права защищены</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
import { Card, CardContent } from "@/components/ui/card";
import Icon from "@/components/ui/icon";

interface ServicesSectionProps {
  scrollToSection: (id: string) => void;
}

const ServicesSection = ({ scrollToSection }: ServicesSectionProps) => {
  const scrollToCategory = (categoryId: string) => {
    const element = document.getElementById(categoryId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  const victoriaServices = [
    {
      category: "Маникюр",
      items: [
        { name: "Маникюр", price: "900 ₽", duration: 40 },
        { name: "Японский маникюр", price: "1100 ₽", duration: 60 },
        { name: "Мужской маникюр", price: "1000 ₽", duration: 40 },
        { name: "Детский маникюр", price: "600 ₽", duration: 35 }
      ]
    },
    {
      category: "Покрытие гель-лаком",
      items: [
        { name: "Снятие гель лака", price: "500 ₽", duration: 30 },
        { name: "Маникюр + покрытие гель лак", price: "1800 ₽", duration: 80 },
        { name: "Снятие, маникюр, покрытие гель лак", price: "2200 ₽", duration: 150 },
        { name: "Дизайн не сложный", price: "500 ₽", duration: 30 },
        { name: "Френч", price: "500 ₽", duration: 30 }
      ]
    },
    {
      category: "Наращивание и гель",
      items: [
        { name: "Маникюр + покрытие гелем (свыше 0,5 мм)", price: "2300 ₽", duration: 100 },
        { name: "Снятие, маникюр, покрытие гелем (свыше 0,5 мм)", price: "2500 ₽", duration: 150 },
        { name: "Наращивание ногтей + маникюр", price: "2500 ₽", duration: 180 },
        { name: "Комплекс (снятие, маникюр, наращивание, покрытие, дизайн)", price: "4000 ₽", duration: 210 },
        { name: "Коррекция нарощенных ногтей", price: "2000 ₽", duration: 120 },
        { name: "Снятие нарощенных ногтей", price: "500 ₽", duration: 30 }
      ]
    },
    {
      category: "Укрепление и ремонт",
      items: [
        { name: "Укрепление ногтей (гелем, акрилом)", price: "1000 ₽", duration: 30 },
        { name: "Ремонт ногтя", price: "150 ₽", duration: 30 }
      ]
    },
    {
      category: "Шугаринг",
      items: [
        { name: "Тотальное бикини", price: "1500 ₽", duration: 40 },
        { name: "Классическое бикини", price: "1000 ₽", duration: 20 },
        { name: "Ноги полностью", price: "1800 ₽", duration: 30 },
        { name: "Голень", price: "900 ₽", duration: 20 },
        { name: "Бедра", price: "1000 ₽", duration: 20 },
        { name: "Руки полностью", price: "1000 ₽", duration: 30 },
        { name: "Руки до локтя", price: "900 ₽", duration: 20 },
        { name: "Подмышки", price: "500 ₽", duration: 15 },
        { name: "Ягодицы", price: "700 ₽", duration: 20 },
        { name: "Спина полностью", price: "1300 ₽", duration: 30 },
        { name: "Поясница", price: "600 ₽", duration: 20 },
        { name: "Депиляция (любая зона на лице)", price: "250 ₽", duration: 15 }
      ]
    }
  ];

  const alenaServices = [
    {
      category: "Массаж",
      items: [
        { name: "LPG 30 минут", price: "1500 ₽", duration: 30 },
        { name: "LPG 40 минут", price: "1900 ₽", duration: 40 },
        { name: "LPG 60 минут", price: "2750 ₽", duration: 60 },
        { name: "Ручной расслабляющий 1 час", price: "3300 ₽", duration: 60 },
        { name: "Ручной расслабляющий 1,5 часа", price: "4400 ₽", duration: 90 },
        { name: "Shot LPG + G5", price: "от 2200 ₽", duration: 60 },
        { name: "Shot LPG 30 мин + G5 20 мин + банки 20 мин", price: "от 2600 ₽", duration: 90 },
        { name: "Shot LPG 30 мин + миостиммуляция 20 мин", price: "от 2000 ₽", duration: 60 },
        { name: "Shot банки 30 мин + LPG 40 мин", price: "от 2400 ₽", duration: 80 },
        { name: "Антицеллюлитный массаж", price: "от 3500 ₽", duration: 60 },
        { name: "Лимфодренажный массаж", price: "от 3000 ₽", duration: 60 },
        { name: "Массаж спины", price: "от 2100 ₽", duration: 30 }
      ]
    },
    {
      category: "Аппаратные процедуры",
      items: [
        { name: "Аренда костюма LPG", price: "от 300 ₽", duration: 5 },
        { name: "Баночный аппаратный «паук»", price: "от 1600 ₽", duration: 30 },
        { name: "Вибро G5 20 минут", price: "от 1500 ₽", duration: 20 },
        { name: "Вибро G5 30 минут", price: "от 1800 ₽", duration: 30 },
        { name: "Горячий вакуум", price: "от 1900 ₽", duration: 30 },
        { name: "Пробный LPG", price: "от 700 ₽", duration: 25 },
        { name: "Ролико вакуумный 30 минут", price: "от 1500 ₽", duration: 30 },
        { name: "Ролико вакуумный 40 минут", price: "от 1900 ₽", duration: 40 }
      ]
    },
    {
      category: "Чистка лица",
      items: [
        { name: "УЗ чистка", price: "1800 ₽", duration: 60 },
        { name: "Комбинированная", price: "от 2500 ₽", duration: 120 },
        { name: "Атравматическая чистка лица", price: "от 3500 ₽", duration: 75 }
      ]
    },
    {
      category: "Кислотные пилинги",
      items: [
        { name: "Высокомолекулярные", price: "от 1800 ₽", duration: 60 },
        { name: "Серединные", price: "от 2500 ₽", duration: 60 },
        { name: "PRX 33", price: "от 4000 ₽", duration: 60 }
      ]
    },
    {
      category: "Уходовые процедуры по лицу",
      items: [
        { name: "Комбинированные уходовые по лицу", price: "от 2500 ₽", duration: 60 },
        { name: "Маска альгинатная", price: "от 1800 ₽", duration: 30 },
        { name: "Ручной массаж лица лимфодреннажный 30 минут", price: "от 2000 ₽", duration: 30 },
        { name: "Ручной массаж лица лимфодреннажный 1 час", price: "от 3000 ₽", duration: 60 },
        { name: "Ручной массаж лица скульптурирующий 40 минут", price: "от 2300 ₽", duration: 40 },
        { name: "Ручной массаж лица скульптурирующий 1 час 10 минут", price: "от 3400 ₽", duration: 70 }
      ]
    }
  ];

  return (
    <>
      <section id="услуги" className="py-20 px-4 bg-black">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <p className="text-accent text-sm tracking-widest mb-4">НАШИ УСЛУГИ</p>
            <h2 className="text-5xl font-light">Спектр возможностей</h2>
          </div>
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { icon: "Sparkles", title: "Ногтевой сервис", desc: "Маникюр, покрытие, наращивание", target: "ногтевой-сервис" },
              { icon: "Waves", title: "Шугаринг", desc: "Все зоны депиляции", target: "шугаринг" },
              { icon: "HandHeart", title: "Массаж", desc: "LPG, ручной, аппаратный", target: "массаж" },
              { icon: "Heart", title: "Уход за лицом", desc: "Чистки, пилинги, уходовые процедуры", target: "лицо" }
            ].map((service, idx) => (
              <Card 
                key={idx} 
                className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 group cursor-pointer"
                onClick={() => scrollToCategory(service.target)}
              >
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

      <section id="прайс" className="py-20 px-4 bg-black">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <p className="text-accent text-sm tracking-widest mb-4">ПРАЙС-ЛИСТ</p>
            <h2 className="text-5xl font-light mb-4 text-white">Стоимость услуг</h2>
          </div>

          <div className="mb-16" id="ногтевой-сервис">
            <h3 className="text-4xl font-bold text-center mb-8 pb-4 border-b-2 border-accent/30 max-w-4xl mx-auto text-white">
              Виктория — Ногтевой сервис
            </h3>
            <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
              {victoriaServices.map((category, idx) => (
                <Card key={idx} className="border border-gray-700 shadow-md bg-zinc-900">
                  <CardContent className="p-8">
                    <h4 className="text-2xl font-light mb-6 pb-4 border-b border-accent/30 text-white">
                      {category.category}
                    </h4>
                    <div className="space-y-4">
                      {category.items.map((item, itemIdx) => (
                        <div key={itemIdx} className="flex justify-between items-start gap-4">
                          <div>
                            <span className="text-white block">{item.name}</span>
                            <span className="text-gray-400 text-sm">{item.duration} мин</span>
                          </div>
                          <span className="text-accent font-medium whitespace-nowrap">{item.price}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          <div className="mb-16" id="шугаринг">
            <h3 className="text-4xl font-bold text-center mb-8 pb-4 border-b-2 border-accent/30 max-w-4xl mx-auto text-white">
              Виктория — Шугаринг
            </h3>
            <div className="max-w-4xl mx-auto">
              <Card className="border border-gray-700 shadow-md bg-zinc-900">
                <CardContent className="p-8">
                  <div className="grid md:grid-cols-2 gap-x-12 gap-y-4">
                    {victoriaServices[4].items.map((item, itemIdx) => (
                      <div key={itemIdx} className="flex justify-between items-start gap-4">
                        <div>
                          <span className="text-white block">{item.name}</span>
                          <span className="text-gray-400 text-sm">{item.duration} мин</span>
                        </div>
                        <span className="text-accent font-medium whitespace-nowrap">{item.price}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          <div className="mb-16" id="массаж">
            <h3 className="text-4xl font-bold text-center mb-8 pb-4 border-b-2 border-accent/30 max-w-4xl mx-auto text-white">
              Алёна — Массаж и аппаратные процедуры
            </h3>
            <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
              {alenaServices.slice(0, 2).map((category, idx) => (
                <Card key={idx} className="border border-gray-700 shadow-md bg-zinc-900">
                  <CardContent className="p-8">
                    <h4 className="text-2xl font-light mb-6 pb-4 border-b border-accent/30 text-white">
                      {category.category}
                    </h4>
                    <div className="space-y-4">
                      {category.items.map((item, itemIdx) => (
                        <div key={itemIdx} className="flex justify-between items-start gap-4">
                          <div>
                            <span className="text-white block">{item.name}</span>
                            <span className="text-gray-400 text-sm">{item.duration} мин</span>
                          </div>
                          <span className="text-accent font-medium whitespace-nowrap">{item.price}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          <div id="лицо">
            <h3 className="text-4xl font-bold text-center mb-8 pb-4 border-b-2 border-accent/30 max-w-4xl mx-auto text-white">
              Алёна — Уход за лицом
            </h3>
            <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
              {alenaServices.slice(2).map((category, idx) => (
                <Card key={idx} className="border border-gray-700 shadow-md bg-zinc-900">
                  <CardContent className="p-8">
                    <h4 className="text-2xl font-light mb-6 pb-4 border-b border-accent/30 text-white">
                      {category.category}
                    </h4>
                    <div className="space-y-4">
                      {category.items.map((item, itemIdx) => (
                        <div key={itemIdx} className="flex justify-between items-start gap-4">
                          <div>
                            <span className="text-white block">{item.name}</span>
                            <span className="text-gray-400 text-sm">{item.duration} мин</span>
                          </div>
                          <span className="text-accent font-medium whitespace-nowrap">{item.price}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>
    </>
  );
};

export default ServicesSection;
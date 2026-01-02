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
    }
  ];

  const alenaServices = [
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
    },
    {
      category: "Чистка лица",
      items: [
        { name: "УЗ чистка", price: "1800 ₽", duration: 60 },
        { name: "Комбинированная", price: "от 2500 ₽", duration: 120 }
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
        { name: "Уходовые процедуры", price: "от 1500 ₽", duration: 60 }
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
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: "Sparkles", title: "Ногтевой сервис", desc: "Маникюр, покрытие, наращивание", target: "ногтевой-сервис" },
              { icon: "Waves", title: "Шугаринг", desc: "Все зоны депиляции", target: "шугаринг" },
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
              Алёна — Шугаринг
            </h3>
            <div className="max-w-4xl mx-auto">
              <Card className="border border-gray-700 shadow-md bg-zinc-900">
                <CardContent className="p-8">
                  <div className="grid md:grid-cols-2 gap-x-12 gap-y-4">
                    {alenaServices[0].items.map((item, itemIdx) => (
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

          <div id="лицо">
            <h3 className="text-4xl font-bold text-center mb-8 pb-4 border-b-2 border-accent/30 max-w-4xl mx-auto text-white">
              Алёна — Уход за лицом
            </h3>
            <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
              {alenaServices.slice(1).map((category, idx) => (
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

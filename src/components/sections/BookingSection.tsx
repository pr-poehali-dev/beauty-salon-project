import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";

const BookingSection = () => {
  const [formData, setFormData] = useState({
    master: "",
    name: "",
    phone: "",
    service: "",
    appointment_date: "",
    appointment_time: "",
    message: ""
  });

  const { toast } = useToast();

  const masterServices = {
    "Виктория": [
      "Аппаратный маникюр",
      "Выравнивание ногтевой пластины",
      "Покрытие с градиентом (омбре)",
      "Детский маникюр",
      "Дизайн ногтей",
      "Коррекция наращённых ногтей",
      "Мужской маникюр",
      "Маникюр с покрытием гель-лаком",
      "Наращивание ногтей",
      "Покрытие ногтей на руках гель-лаком",
      "Покрытие ногтей на руках биогелем",
      "Ремонт ногтя",
      "Снятие биогеля",
      "Снятие гель-лака с ногтей на руках",
      "Снятие наращённых ногтей",
      "Укрепление ногтей",
      "Японский маникюр",
      "Депиляция"
    ],
    "Алёна": [
      "LPG массаж",
      "Лимфодренажный массаж",
      "Прессотерапия",
      "Чистка лица",
      "Биоревитализация",
      "Уходовые процедуры по лицу"
    ]
  };



  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await fetch('https://functions.poehali.dev/84a78be2-981d-4e9e-bf2a-9d3c080f94bc', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          master: formData.master,
          client_name: formData.name,
          client_phone: formData.phone,
          service: formData.service,
          appointment_date: formData.appointment_date,
          appointment_time: formData.appointment_time,
          message: formData.message
        }),
      });

      const result = await response.json();

      if (result.success) {
        toast({
          title: "Запись создана!",
          description: `Вы записаны к мастеру ${formData.master} на ${formData.appointment_date} в ${formData.appointment_time}`,
        });
        setFormData({ master: "", name: "", phone: "", service: "", appointment_date: "", appointment_time: "", message: "" });
      } else {
        toast({
          title: "Ошибка",
          description: result.error || "Не удалось создать запись. Попробуйте позже.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Ошибка",
        description: "Не удалось создать запись. Попробуйте позже.",
        variant: "destructive",
      });
    }
  };

  return (
    <section id="запись" className="py-20 px-4 bg-black">
      <div className="container mx-auto max-w-2xl">
        <div className="text-center mb-12">
          <p className="text-accent text-sm tracking-widest mb-4">ОНЛАЙН ЗАПИСЬ</p>
          <h2 className="text-5xl font-light mb-4 text-white">Записаться на прием</h2>
          <p className="text-white mb-6">Выберите мастера, услугу и удобное время</p>
          <a 
            href="https://t.me/promisslab" 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center gap-3 px-6 py-3 bg-accent text-black rounded-lg hover:bg-accent/90 transition-all font-medium text-base"
          >
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.295-.6.295-.002 0-.003 0-.005 0l.213-3.054 5.56-5.022c.24-.213-.054-.334-.373-.121l-6.869 4.326-2.96-.924c-.64-.203-.658-.64.135-.954l11.566-4.458c.538-.196 1.006.128.832.941z"/>
            </svg>
            Записаться через Telegram бот
          </a>
          <p className="text-white/60 text-sm mt-4">или заполните форму ниже</p>
        </div>
        <Card className="border-0 shadow-xl bg-white">
          <CardContent className="p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <Label htmlFor="master" className="text-sm tracking-wider">МАСТЕР *</Label>
                <Select 
                  value={formData.master} 
                  onValueChange={(value) => setFormData({ ...formData, master: value, service: "", appointment_time: "" })}
                  required
                >
                  <SelectTrigger className="mt-2">
                    <SelectValue placeholder="Выберите мастера" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Виктория">Виктория (маникюр, депиляция)</SelectItem>
                    <SelectItem value="Алёна">Алёна (массаж, уход за лицом)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {formData.master && (
                <div>
                  <Label htmlFor="service" className="text-sm tracking-wider">УСЛУГА *</Label>
                  <Select 
                    value={formData.service} 
                    onValueChange={(value) => setFormData({ ...formData, service: value })}
                    required
                  >
                    <SelectTrigger className="mt-2">
                      <SelectValue placeholder="Выберите услугу" />
                    </SelectTrigger>
                    <SelectContent>
                      {masterServices[formData.master as keyof typeof masterServices].map((service) => (
                        <SelectItem key={service} value={service}>{service}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="date" className="text-sm tracking-wider">ДАТА *</Label>
                  <Input
                    id="date"
                    type="date"
                    value={formData.appointment_date}
                    onChange={(e) => setFormData({ ...formData, appointment_date: e.target.value, appointment_time: "" })}
                    min={new Date().toISOString().split('T')[0]}
                    required
                    className="mt-2"
                    disabled={!formData.master}
                  />
                </div>

                <div>
                  <Label htmlFor="time" className="text-sm tracking-wider">ВРЕМЯ *</Label>
                  <Input
                    id="time"
                    type="time"
                    value={formData.appointment_time}
                    onChange={(e) => setFormData({ ...formData, appointment_time: e.target.value })}
                    required
                    className="mt-2"
                    disabled={!formData.appointment_date}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="name" className="text-sm tracking-wider">ВАШЕ ИМЯ *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="mt-2"
                  placeholder="Введите имя"
                />
              </div>

              <div>
                <Label htmlFor="phone" className="text-sm tracking-wider">ТЕЛЕФОН *</Label>
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
                disabled={!formData.master || !formData.service || !formData.appointment_date || !formData.appointment_time}
              >
                ЗАПИСАТЬСЯ
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default BookingSection;
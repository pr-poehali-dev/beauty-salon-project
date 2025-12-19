import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Icon from "@/components/ui/icon";
import { useToast } from "@/hooks/use-toast";

interface Booking {
  id: number;
  name: string;
  phone: string;
  service: string;
  message: string;
  created_at: string;
}

const Admin = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  const loadBookings = async () => {
    try {
      setLoading(true);
      const response = await fetch('https://functions.poehali.dev/e7cf85f5-775b-41b8-a953-d09953b8825c');
      const data = await response.json();
      
      if (data.success) {
        setBookings(data.bookings);
      } else {
        toast({
          title: "Ошибка",
          description: "Не удалось загрузить заявки",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Ошибка",
        description: "Не удалось загрузить заявки",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBookings();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <div className="min-h-screen bg-secondary/30 p-8">
      <div className="container mx-auto max-w-7xl">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-light mb-2">Панель администратора</h1>
            <p className="text-muted-foreground">Управление заявками на запись</p>
          </div>
          <Button onClick={loadBookings} disabled={loading}>
            <Icon name="RefreshCw" size={18} className="mr-2" />
            Обновить
          </Button>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Icon name="BarChart3" size={24} />
              Статистика
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <p className="text-muted-foreground text-sm mb-1">Всего заявок</p>
                <p className="text-3xl font-light">{bookings.length}</p>
              </div>
              <div>
                <p className="text-muted-foreground text-sm mb-1">За сегодня</p>
                <p className="text-3xl font-light">
                  {bookings.filter(b => {
                    const today = new Date().toDateString();
                    const bookingDate = new Date(b.created_at).toDateString();
                    return today === bookingDate;
                  }).length}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground text-sm mb-1">За неделю</p>
                <p className="text-3xl font-light">
                  {bookings.filter(b => {
                    const weekAgo = new Date();
                    weekAgo.setDate(weekAgo.getDate() - 7);
                    return new Date(b.created_at) > weekAgo;
                  }).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {loading ? (
          <div className="text-center py-12">
            <Icon name="Loader2" size={48} className="mx-auto animate-spin text-accent" />
            <p className="mt-4 text-muted-foreground">Загрузка заявок...</p>
          </div>
        ) : bookings.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <Icon name="Inbox" size={48} className="mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">Пока нет заявок</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {bookings.map((booking) => (
              <Card key={booking.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="grid md:grid-cols-[1fr,auto] gap-6">
                    <div className="space-y-3">
                      <div className="flex items-start gap-3">
                        <Icon name="User" size={20} className="text-accent mt-1" />
                        <div>
                          <p className="text-sm text-muted-foreground">Имя</p>
                          <p className="text-lg font-medium">{booking.name}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-start gap-3">
                        <Icon name="Phone" size={20} className="text-accent mt-1" />
                        <div>
                          <p className="text-sm text-muted-foreground">Телефон</p>
                          <a href={`tel:${booking.phone}`} className="text-lg hover:text-accent transition-colors">
                            {booking.phone}
                          </a>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <Icon name="Scissors" size={20} className="text-accent mt-1" />
                        <div>
                          <p className="text-sm text-muted-foreground">Услуга</p>
                          <p className="text-lg">{booking.service}</p>
                        </div>
                      </div>

                      {booking.message && (
                        <div className="flex items-start gap-3">
                          <Icon name="MessageSquare" size={20} className="text-accent mt-1" />
                          <div>
                            <p className="text-sm text-muted-foreground">Сообщение</p>
                            <p className="text-lg">{booking.message}</p>
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="flex flex-col items-end justify-between">
                      <div className="text-right">
                        <p className="text-sm text-muted-foreground mb-1">Заявка #{booking.id}</p>
                        <p className="text-sm text-muted-foreground flex items-center gap-1">
                          <Icon name="Calendar" size={16} />
                          {formatDate(booking.created_at)}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Admin;
